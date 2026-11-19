"""Unit tests of ai/train/evaluate.py with a synthetic YOLO dataset and a fake model (no GPU).

    python -m pytest ai/train/tests -q
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest
from PIL import Image

APP_ROOT = Path(__file__).resolve().parents[3]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from ai.train import evaluate as ev  # noqa: E402

NAMES = {0: "no_helmet", 1: "no_vest", 2: "helmet"}


# ---------------------------------------------------------------------------
# metrics and gate (NFR-01)
# ---------------------------------------------------------------------------


def test_image_level_metrics_counts_images_not_boxes():
    m = ev.image_level_metrics([True, True, False, False], [True, False, True, False])
    assert (m["tp"], m["fn"], m["fp"], m["tn"]) == (1, 1, 1, 1)
    assert m["recall"] == 0.5 and m["precision"] == 0.5


def test_image_level_metrics_without_positives_is_zero():
    m = ev.image_level_metrics([False, False], [False, False])
    assert m["recall"] == 0.0 and m["precision"] == 0.0


@pytest.mark.parametrize("tp, expected", [(79, False), (80, True), (81, True)])
def test_hardhat_gate_boundary_at_80_percent(tp, expected):
    # 100 positive images, tp of them found; precision kept at or above 0.80
    actual = [True] * 100 + [False] * 100
    predicted = [True] * tp + [False] * (100 - tp) + [True] * 10 + [False] * 90
    metrics = ev.image_level_metrics(actual, predicted)
    assert metrics["recall"] == tp / 100
    assert ev.passes_hardhat_gate(metrics) is expected


def test_hardhat_gate_needs_precision_too():
    assert ev.passes_hardhat_gate({"recall": 0.95, "precision": 0.79}) is False
    assert ev.passes_hardhat_gate({"recall": 0.80, "precision": 0.80}) is True


@pytest.mark.parametrize("positive, negative", [(99, 100), (100, 99), (0, 500)])
def test_test_set_needs_100_images_per_group(positive, negative):
    with pytest.raises(ValueError):
        ev.validate_test_size(positive, negative)


def test_test_set_of_100_and_100_is_enough():
    ev.validate_test_size(100, 100)


# ---------------------------------------------------------------------------
# threshold.json and classes.json
# ---------------------------------------------------------------------------


def test_read_threshold_from_validation_split(tmp_path):
    path = tmp_path / "threshold.json"
    path.write_text(json.dumps({"conf_threshold": 0.35, "split": "val"}))
    assert ev.read_threshold(path) == 0.35


@pytest.mark.parametrize("document", [
    {"conf_threshold": 1.2},
    {"conf_threshold": True},
    {"conf_threshold": 0.4, "split": "test"},     # a threshold tuned on the test set is refused
    {"conf_threshold": 0.4, "threshold": 0.5},
    [0.4],
])
def test_read_threshold_rejects_bad_documents(tmp_path, document):
    path = tmp_path / "threshold.json"
    path.write_text(json.dumps(document))
    with pytest.raises(ValueError):
        ev.read_threshold(path)


def test_class_aliases_and_ids(tmp_path):
    path = tmp_path / "classes.json"
    path.write_text(json.dumps({"NO_HARDHAT": ["No_Helmet", "no-hardhat"], "NO_VEST": "no_vest"}))
    aliases = ev.read_class_aliases(path)
    ids, known = ev.class_ids(NAMES, aliases, "model")
    assert ids == {"NO_HARDHAT": {0}, "NO_VEST": {1}} and known == {0, 1, 2}
    ids, _ = ev.class_ids(["no_helmet", "no_vest"], aliases, "list names")
    assert ids == {"NO_HARDHAT": {0}, "NO_VEST": {1}}


def test_class_aliases_must_be_distinct_and_present(tmp_path):
    path = tmp_path / "classes.json"
    path.write_text(json.dumps({"NO_HARDHAT": "x", "NO_VEST": "X"}))
    with pytest.raises(ValueError):
        ev.read_class_aliases(path)
    path.write_text(json.dumps({"NO_HARDHAT": "x", "NO_VEST": "y"}))
    with pytest.raises(ValueError):
        ev.class_ids(NAMES, ev.read_class_aliases(path), "model")


def test_shipped_classes_json_is_valid():
    aliases = ev.read_class_aliases(Path(ev.__file__).with_name("classes.json"))
    assert set(aliases) == {"NO_HARDHAT", "NO_VEST"}


# ---------------------------------------------------------------------------
# synthetic YOLO dataset
# ---------------------------------------------------------------------------


def make_dataset(root: Path, positives=100, negatives=100, vest_every=3):
    """images/test/{i}.png with pixel (i % 256, i // 256, 0) so a fake model can tell images apart."""
    for split in ("train", "val", "test"):
        (root / "images" / split).mkdir(parents=True)
        (root / "labels" / split).mkdir(parents=True)
    for split in ("train", "val"):
        Image.new("RGB", (4, 4)).save(root / "images" / split / "x.png")
    for i in range(positives + negatives):
        Image.new("RGB", (4, 4), (i % 256, i // 256, 0)).save(root / "images" / "test" / f"{i:04d}.png")
        lines = []
        if i < positives:
            lines.append("0 0.5 0.5 0.2 0.2")
        if i % vest_every == 0:
            lines.append("1 0.3 0.3 0.1 0.1")
        lines.append("2 0.7 0.7 0.1 0.1")  # a helmet: not a PPE problem class
        (root / "labels" / "test" / f"{i:04d}.txt").write_text("\n".join(lines) + "\n")
    data = root / "data.yaml"
    data.write_text(
        "path: .\ntrain: images/train\nval: images/val\ntest: images/test\n"
        "names:\n  0: no_helmet\n  1: no_vest\n  2: helmet\n",
        encoding="utf-8",
    )
    return data


def aliases():
    return {"NO_HARDHAT": {"no_helmet"}, "NO_VEST": {"no_vest"}}


def test_load_test_set_reads_labels(tmp_path):
    images, actual = ev.load_test_set(make_dataset(tmp_path), aliases())
    assert len(images) == 200
    assert sum(actual["NO_HARDHAT"]) == 100
    assert sum(actual["NO_VEST"]) == len(range(0, 200, 3))


def test_load_test_set_refuses_small_test_set(tmp_path):
    with pytest.raises(ValueError, match="at least 100"):
        ev.load_test_set(make_dataset(tmp_path, positives=99), aliases())


def test_load_test_set_refuses_overlap_with_train(tmp_path):
    data = make_dataset(tmp_path)
    data.write_text(data.read_text().replace("train: images/train", "train: images/test"))
    with pytest.raises(ValueError, match="shares image paths"):
        ev.load_test_set(data, aliases())


def test_invalid_label_line_is_reported(tmp_path):
    data = make_dataset(tmp_path)
    (tmp_path / "labels" / "test" / "0005.txt").write_text("7 0.5 0.5 0.2 0.2\n")
    with pytest.raises(ValueError, match="invalid YOLO detection label"):
        ev.load_test_set(data, aliases())


def test_missing_label_file_is_a_background_image(tmp_path):
    data = make_dataset(tmp_path, positives=100, negatives=101)
    (tmp_path / "labels" / "test" / "0200.txt").unlink()
    images, actual = ev.load_test_set(data, aliases())
    assert actual["NO_HARDHAT"][-1] is False and actual["NO_VEST"][-1] is False


# ---------------------------------------------------------------------------
# evaluate() / main() with a fake ultralytics + torch
# ---------------------------------------------------------------------------


class _T(list):
    def tolist(self):
        return list(self)


class _Device:
    type = "cpu"

    def __str__(self):
        return "cpu"


def install_fake_model(monkeypatch, found_positive: int, false_positive: int, score=0.9):
    """Model 'sees' no_helmet on the first `found_positive` positives and on `false_positive` negatives."""

    class YOLO:
        names = NAMES

        def __init__(self, path, task):
            self.predictor = types.SimpleNamespace(device=_Device())

        def predict(self, source, conf, classes, imgsz, device, verbose):
            r, g, _ = source.getpixel((0, 0))
            i = g * 256 + r
            hit = i < found_positive or 100 <= i < 100 + false_positive
            cls, confs = ([0], [score]) if hit else ([], [])
            if i % 3 == 0:
                cls, confs = cls + [1], confs + [0.95]
            boxes = types.SimpleNamespace(cls=_T(cls), conf=_T(confs))
            return [types.SimpleNamespace(boxes=boxes)]

    ultralytics = types.ModuleType("ultralytics")
    ultralytics.YOLO = YOLO
    torch = types.ModuleType("torch")
    torch.cuda = types.SimpleNamespace(get_device_name=lambda device: "fake-gpu")
    monkeypatch.setitem(sys.modules, "ultralytics", ultralytics)
    monkeypatch.setitem(sys.modules, "torch", torch)


def cli_args(tmp_path, threshold=0.5):
    data = make_dataset(tmp_path / "ds")
    model = tmp_path / "best.pt"
    model.write_bytes(b"weights")
    th = tmp_path / "threshold.json"
    th.write_text(json.dumps({"conf_threshold": threshold, "split": "val"}))
    classes = tmp_path / "classes.json"
    classes.write_text(json.dumps({"NO_HARDHAT": "no_helmet", "NO_VEST": "no_vest"}))
    out = tmp_path / "metrics.json"
    return out, [
        "--data", str(data), "--model", str(model), "--model-version", "ppe-yolo-v1",
        "--threshold", str(th), "--classes", str(classes), "--device", "cpu", "--output", str(out),
    ]


@pytest.mark.parametrize("found, code", [(79, 1), (80, 0), (81, 0)])
def test_main_writes_metrics_and_exit_code_follows_gate(tmp_path, monkeypatch, capsys, found, code):
    install_fake_model(monkeypatch, found_positive=found, false_positive=20)
    out, argv = cli_args(tmp_path)
    assert ev.main(argv) == code
    report = json.loads(out.read_text(encoding="utf-8"))
    hard = report["classes"]["NO_HARDHAT"]
    assert (hard["tp"], hard["fn"], hard["fp"]) == (found, 100 - found, 20)
    assert report["passed"] is (code == 0)
    assert report["image_count"] == 200 and report["split"] == "test"
    assert report["model_version"] == "ppe-yolo-v1" and report["conf_threshold"] == 0.5
    assert report["classes"]["NO_VEST"]["recall"] == 1.0
    assert ("ผ่าน" if code == 0 else "ไม่ผ่านเกณฑ์") in capsys.readouterr().out


def test_score_equal_to_threshold_counts(tmp_path, monkeypatch):
    install_fake_model(monkeypatch, found_positive=100, false_positive=0, score=0.5)
    out, argv = cli_args(tmp_path, threshold=0.5)
    assert ev.main(argv) == 0
    assert json.loads(out.read_text())["classes"]["NO_HARDHAT"]["tp"] == 100


def test_score_below_threshold_is_dropped(tmp_path, monkeypatch):
    install_fake_model(monkeypatch, found_positive=100, false_positive=0, score=0.49)
    out, argv = cli_args(tmp_path, threshold=0.5)
    assert ev.main(argv) == 1
    assert json.loads(out.read_text())["classes"]["NO_HARDHAT"]["tp"] == 0


def test_main_reports_missing_checkpoint(tmp_path, monkeypatch):
    install_fake_model(monkeypatch, found_positive=100, false_positive=0)
    out, argv = cli_args(tmp_path)
    (tmp_path / "best.pt").unlink()
    with pytest.raises(SystemExit) as exc:
        ev.main(argv)
    assert exc.value.code == 2 and not out.exists()
