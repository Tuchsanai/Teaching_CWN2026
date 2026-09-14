#!/usr/bin/env python3
"""Run the unchanged LAB run-scenarios.py suite against both UI versions."""
import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'tests')
    args = parser.parse_args()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    lab = ROOT / '006_LAB_Test_Scenarios_Traceability'
    scenarios = lab / 'input/ui-scenarios.json'
    fixture = json.loads(scenarios.read_text())
    cases = fixture['scenarios'] if isinstance(fixture, dict) else fixture
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    reports = out / 'runs' / run_id
    reports.mkdir(parents=True)
    ui = {}
    infrastructure_failed = False
    for version, html in (
        ('v1', ROOT / '004_LAB_Conditional_Graph_UI_Mockup/reference/final/ui-mockup.html'),
        ('v2', ROOT / '005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-mockup-v2.html'),
    ):
        shots = out / 'screenshots' / f'ui-{version}'
        # Preserve prior runs in their own directory before publishing latest shots.
        if shots.exists():
            shots.rename(reports / f'previous-ui-{version}')
        raw = reports / f'ui-{version}.json'
        command = [sys.executable, '-B', str(lab / 'tests/run-scenarios.py'),
                   '--html', str(html), '--scenarios', str(scenarios),
                   '--out', str(raw), '--shots', str(shots), '--allow-fail']
        completed = subprocess.run(command, capture_output=True, text=True)
        if not raw.exists():
            raise RuntimeError(f'{version}: runner produced no report: {completed.stderr}')
        report = json.loads(raw.read_text())
        for case, result in zip(cases, report['results']):
            result['reason'] = result['reason'].replace(str(ROOT.parent), '<PROJECT_ROOT>')
            if result['screenshot']:
                result['screenshot'] = str(Path(result['screenshot']).relative_to(out))
            if result['status'] == 'fail':
                us = case.get('us')
                if version == 'v1' and us in ('US-09', 'US-14', 'US-21'):
                    result['diagnosis'] = 'ฟีเจอร์ที่เพิ่มใน UI v2; เก็บผลตกบน UI v1 ตามชุด scenario เดิม'
                elif us == 'US-09':
                    result['diagnosis'] = 'fixture mismatch: payment-summary-total ไม่มีใน UI v2 (รายงานเดิม F01)'
                elif us == 'US-21':
                    result['diagnosis'] = 'fixture mismatch: rush-start ไม่มี และขาดขั้น nav-capacity (รายงานเดิม F02)'
                else:
                    result['diagnosis'] = 'ดู assertion และภาพที่ runner บันทึก'
            if not result['screenshot'] and result['status'] != 'skip':
                infrastructure_failed = True
        report['html'] = str(html.relative_to(ROOT))
        if report.get('launch_fallback_reason'):
            report['launch_fallback_reason'] = report['launch_fallback_reason'].replace(str(ROOT.parent), '<PROJECT_ROOT>')
        report['timestamp_thai'] = datetime.now(timezone(timedelta(hours=7))).isoformat()
        # The runner JSON is new QA output; publish portable paths only.
        raw.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        ui[version] = report
        infrastructure_failed |= completed.returncode != 0 or len(report['results']) != len(cases)
        print(version, {k: report[k] for k in ('passed', 'failed', 'skipped')})
    result_path = out / 'results.json'
    results = json.loads(result_path.read_text()) if result_path.exists() else {}
    results['ui'] = ui
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    # Failed product/fixture cases remain visible, as with --allow-fail upstream.
    return int(infrastructure_failed)


if __name__ == '__main__':
    raise SystemExit(main())
