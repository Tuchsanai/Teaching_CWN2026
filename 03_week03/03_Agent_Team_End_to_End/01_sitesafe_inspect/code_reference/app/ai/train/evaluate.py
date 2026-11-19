"""Evaluate a YOLO detection checkpoint on the held-out test split."""

import argparse
import json
from math import isfinite
from os import sep
from pathlib import Path


PPE_CLASSES = ("NO_HARDHAT", "NO_VEST")
MIN_TEST_IMAGES_PER_GROUP = 100
MIN_METRIC = 0.80
IMAGE_EXTENSIONS = {
    ".bmp", ".dng", ".heic", ".jpeg", ".jpg", ".mpo", ".pfm", ".png",
    ".tif", ".tiff", ".webp",
}


def image_level_metrics(actual, predicted):
    """Count images with at least one instance of the class on each side."""
    tp = fn = fp = tn = 0
    for present, detected in zip(actual, predicted, strict=True):
        if present and detected:
            tp += 1
        elif present:
            fn += 1
        elif detected:
            fp += 1
        else:
            tn += 1
    return {
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
    }


def passes_hardhat_gate(metrics):
    return metrics["recall"] >= MIN_METRIC and metrics["precision"] >= MIN_METRIC


def validate_test_size(positive, negative):
    if min(positive, negative) < MIN_TEST_IMAGES_PER_GROUP:
        raise ValueError(
            f"Test set needs at least {MIN_TEST_IMAGES_PER_GROUP} NO_HARDHAT "
            f"positive and {MIN_TEST_IMAGES_PER_GROUP} negative images "
            f"(found {positive} positive, {negative} negative)"
        )


def read_threshold(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected a JSON object with conf_threshold")
    threshold = document.get("conf_threshold", document.get("threshold"))
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0 <= threshold <= 1
    ):
        raise ValueError(f"{path}: conf_threshold must be a number between 0 and 1")
    if "threshold" in document and document["threshold"] != threshold:
        raise ValueError(f"{path}: threshold and conf_threshold disagree")
    if document.get("split", "val") not in ("val", "validation"):
        raise ValueError(f"{path}: the threshold must come from the validation split")
    return float(threshold)


def read_class_aliases(path):
    mapping = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict):
        raise ValueError(f"{path}: expected an object keyed by {', '.join(PPE_CLASSES)}")
    aliases = {}
    for name in PPE_CLASSES:
        values = mapping.get(name)
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"{path}: {name} needs a class name or a list of class names")
        aliases[name] = {value.strip().casefold() for value in values}
    if aliases["NO_HARDHAT"] & aliases["NO_VEST"]:
        raise ValueError(f"{path}: NO_HARDHAT and NO_VEST must use distinct class names")
    return aliases


def class_ids(names, aliases, source):
    if isinstance(names, list):
        names = dict(enumerate(names))
    if not isinstance(names, dict) or any(not isinstance(name, str) for name in names.values()):
        raise ValueError(f"{source}: expected class names as a list or ID-to-name mapping")
    names = {int(index): name.strip().casefold() for index, name in names.items()}
    ids = {
        category: {index for index, name in names.items() if name in accepted}
        for category, accepted in aliases.items()
    }
    for category, matching_ids in ids.items():
        if not matching_ids:
            raise ValueError(f"{source}: no class name matches {category}")
    return ids, set(names)


def split_images(root, entries):
    if isinstance(entries, str):
        entries = [entries]
    if not isinstance(entries, list) or not entries or any(
        not isinstance(entry, str) or not entry.strip() for entry in entries
    ):
        raise ValueError("Each dataset split needs an image directory or image-list file")
    images = {}
    for entry in entries:
        source = root / entry
        if source.is_dir():
            candidates = (
                path for path in source.rglob("*")
                if path.suffix.lower() in IMAGE_EXTENSIONS
            )
        elif source.suffix.lower() == ".txt":
            candidates = (
                source.parent / line.strip()
                for line in source.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        else:
            raise ValueError(f"Expected a split directory or image-list file: {source}")
        for path in candidates:
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                raise ValueError(f"Invalid image entry: {path}")
            images.setdefault(path.resolve(), path)
    return images


def label_classes(image, known_ids):
    root, images_dir, relative_path = str(image).rpartition(f"{sep}images{sep}")
    label = Path(root + sep, "labels", relative_path) if images_dir else image
    label = label.with_suffix(".txt")
    try:
        lines = label.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return set()  # YOLO background images may have no annotation file.

    present = set()
    for number, line in enumerate(lines, 1):
        fields = line.split()
        if not fields:
            continue
        try:
            index = int(fields[0])
            if len(fields) != 5 or index not in known_ids:
                raise ValueError
            if not all(isfinite(float(value)) for value in fields[1:]):
                raise ValueError
        except ValueError as error:
            raise ValueError(f"{label}:{number}: invalid YOLO detection label") from error
        present.add(index)
    return present


def load_test_set(path, aliases, enforce_size=True):
    import yaml

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid dataset YAML: {error}") from error
    if not isinstance(data, dict) or not data.get("test"):
        raise ValueError(f"{path}: data.yaml must define a test split")
    dataset_path = data.get("path") or ""
    if not isinstance(dataset_path, str):
        raise ValueError(f"{path}: path must be a dataset directory")
    root = path.absolute().parent / dataset_path
    images = split_images(root, data["test"])
    for split in ("train", "val"):
        if data.get(split) and images.keys() & split_images(root, data[split]).keys():
            raise ValueError(f"Test split shares image paths with the {split} split")

    ids, known_ids = class_ids(data.get("names"), aliases, path)
    images = sorted(images.values())
    actual = {name: [] for name in PPE_CLASSES}
    for image in images:
        present = label_classes(image, known_ids)
        for name in PPE_CLASSES:
            actual[name].append(bool(present & ids[name]))
    positive = sum(actual["NO_HARDHAT"])
    if enforce_size:
        validate_test_size(positive, len(images) - positive)
    return images, actual


def predict_test_set(model, images, ids, threshold, imgsz, device):
    from PIL import Image

    predicted = {name: [] for name in PPE_CLASSES}
    target_ids = sorted(set().union(*ids.values()))
    # YOLO prefilters with >. Apply the inclusive comparison to returned scores.
    prefilter = max(0.0, threshold - 1e-7)
    for path in images:
        with Image.open(path) as source, source.convert("RGB") as image:
            (result,) = model.predict(
                source=image, conf=prefilter, classes=target_ids,
                imgsz=imgsz, device=device, verbose=False,
            )
        if result.boxes is None:
            raise ValueError(f"Model did not return detection boxes for {path}")
        detected = {
            int(index) for index, score in zip(
                result.boxes.cls.tolist(), result.boxes.conf.tolist(), strict=True,
            ) if score >= threshold
        }
        for name in PPE_CLASSES:
            predicted[name].append(bool(detected & ids[name]))
    return predicted


def evaluate(args):
    threshold = read_threshold(args.threshold)
    aliases = read_class_aliases(args.classes)
    allow_small = getattr(args, "allow_small_test", False)
    images, actual = load_test_set(args.data, aliases, enforce_size=not allow_small)
    positive = sum(actual["NO_HARDHAT"])
    negative = len(images) - positive
    size_ok = min(positive, negative) >= MIN_TEST_IMAGES_PER_GROUP

    if not args.model.is_file():
        raise ValueError(f"Model checkpoint does not exist: {args.model}")

    import torch
    from ultralytics import YOLO

    model = YOLO(str(args.model), task="detect")
    ids, _ = class_ids(model.names, aliases, args.model)
    predicted = predict_test_set(model, images, ids, threshold, args.imgsz, args.device)
    classes = {
        name: image_level_metrics(actual[name], predicted[name]) for name in PPE_CLASSES
    }
    metrics_pass = passes_hardhat_gate(classes["NO_HARDHAT"])
    # NFR-01: the gate is only decided on a test set that meets the size condition.
    passed = metrics_pass and size_ok
    if passed:
        result = "ผ่าน"
    elif size_ok:
        result = "ไม่ผ่านเกณฑ์"
    else:
        verdict = "ถึงเกณฑ์" if metrics_pass else "ไม่ถึงเกณฑ์"
        result = f"ยังตัดสินไม่ได้ (Test Set ไม่ครบเงื่อนไข NFR-01 · ค่าที่วัดได้{verdict})"
    device = model.predictor.device
    return {
        "split": "test",
        "image_count": len(images),
        "conf_threshold": threshold,
        "model_version": args.model_version,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "positive_images": positive,
        "negative_images": negative,
        "min_images_per_group": MIN_TEST_IMAGES_PER_GROUP,
        "test_size_ok": size_ok,
        "classes": classes,
        "metrics_pass": metrics_pass,
        "passed": passed,
        "result": result,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="YOLO data.yaml with a test split")
    parser.add_argument("--model", "--weights", type=Path, required=True, help="Path to best.pt")
    parser.add_argument("--model-version", required=True, help="Version reported by the worker")
    parser.add_argument(
        "--threshold", type=Path, default=Path("threshold.json"),
        help="JSON threshold selected on the validation split",
    )
    parser.add_argument(
        "--classes", type=Path, default=Path(__file__).with_name("classes.json"),
        help="JSON model class names keyed by NO_HARDHAT and NO_VEST",
    )
    parser.add_argument(
        "--allow-small-test", action="store_true",
        help="Measure and report even when the test set is below the NFR-01 size "
             "condition (the gate is then reported as not decided, never as passed)",
    )
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", help="Ultralytics device, e.g. 0 or cpu")
    parser.add_argument("--output", type=Path, default=Path("metrics.json"))
    args = parser.parse_args(argv)
    try:
        report = evaluate(args)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (ImportError, OSError, ValueError) as error:
        parser.error(str(error))
    print(f"{report['result']} ({args.output})")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
