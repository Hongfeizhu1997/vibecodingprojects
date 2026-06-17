#!/usr/bin/env python3
"""
GPS Cost Pricing Workbench — Automated Test Runner
====================================================
Extensible framework for validating Stage 3-6 functionality.
Add new test cases in tests/specs/*.yaml — no runner changes needed.

Usage:
  python3 tests/run_tests.py                    # All tests
  python3 tests/run_tests.py --stage 3          # Stage 3 only
  python3 tests/run_tests.py --type static      # Static checks only
  python3 tests/run_tests.py --report md        # Markdown report
"""

import os, sys, json, subprocess, re, csv
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = "/root/ClaudeProjects/GPS_Cost_Pricing_Workbench"
TEST_DIR = os.path.join(PROJECT_ROOT, "tests")
REPORT_DIR = os.path.join(TEST_DIR, "reports")

def _unquote(s):
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

class TestRunner:
    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "skipped": 0, "cases": []}
        self.project = PROJECT_ROOT
    
    def run(self, stage=None, test_type=None):
        """Run all test specs, optionally filtered by stage or type."""
        print("=" * 60)
        print("GPS Cost Pricing Workbench — Test Suite")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        specs_dir = os.path.join(TEST_DIR, "specs")
        for fname in sorted(os.listdir(specs_dir)):
            if not fname.endswith(".yaml"):
                continue
            
            stage_name = fname.replace(".yaml", "")
            if stage and stage not in stage_name:
                continue
            
            self._run_spec(os.path.join(specs_dir, fname), stage_name, test_type)
        
        self._print_summary()
        self._generate_report()
    
    def _run_spec(self, path, stage_name, test_type=None):
        """Parse a YAML spec and run its test cases."""
        spec = self._parse_spec(path)
        if not spec:
            return
        
        print(f"\n{'─' * 50}")
        print(f"  {spec.get('name', stage_name)}")
        print(f"  {spec.get('description', '')}")
        print(f"{'─' * 50}")
        
        for section in spec.get("sections", []):
            section_type = section.get("type", "")
            if test_type and test_type != section_type:
                continue
            
            section_name = section.get("name", section_type)
            print(f"\n  [{section_type.upper()}] {section_name}")
            
            for case in section.get("cases", []):
                self._run_case(case, stage_name, section_type)
    
    def _parse_spec(self, path):
        """Simple YAML-like parser (no PyYAML dependency)."""
        with open(path) as f:
            content = f.read()
        
        spec = {"name": "", "description": "", "sections": []}
        current_section = None
        current_case = None
        
        in_logic = False
        for line in content.split("\n"):
            stripped = line.strip()
            
            # Multi-line logic collection
            if in_logic and current_case:
                if stripped.startswith("- case:") or stripped.startswith("- section:"):
                    in_logic = False
                    current_case.pop("_collecting_logic", None)
                    # fall through to process this line normally
                else:
                    if current_case.get("logic") is not None:
                        current_case["logic"] += "\n" + line.rstrip()
                    continue
            
            if not stripped or stripped.startswith("#"):
                continue
            
            # Top-level fields
            if line.startswith("name:"):
                spec["name"] = _unquote(stripped[5:].strip())
            elif line.startswith("description:"):
                spec["description"] = _unquote(stripped[12:].strip())
            elif stripped.startswith("- section:"):
                current_section = {"name": _unquote(stripped[10:].strip()), "type": "", "cases": []}
                spec["sections"].append(current_section)
                current_case = None
            elif current_section and stripped.startswith("type:"):
                current_section["type"] = stripped[5:].strip()
            elif current_section and stripped.startswith("- case:"):
                current_case = {"name": _unquote(stripped[9:].strip())}
                current_section["cases"].append(current_case)
            elif current_case and stripped.startswith("check:"):
                current_case["check"] = _unquote(stripped[7:].strip())
            elif current_case and stripped.startswith("expect:"):
                current_case["expect"] = _unquote(stripped[8:].strip())
            elif current_case and stripped.startswith("file:"):
                current_case["file"] = _unquote(stripped[6:].strip())
            elif current_case and stripped.startswith("fn:"):
                current_case["fn"] = _unquote(stripped[4:].strip())
            elif current_case and stripped.startswith("args:"):
                current_case["args"] = _unquote(stripped[6:].strip())
            elif current_case and stripped.startswith("logic:"):
                # Multi-line logic: collect lines until next section marker
                val = _unquote(stripped[7:].strip())
                current_case["logic"] = val if val != '|' else ''
                current_case["_collecting_logic"] = val == '|'
                if val == '|':
                    current_case["logic"] = ''
                    in_logic = True
        
        return spec
    
    def _run_case(self, case, stage_name, section_type):
        name = case.get("name", "unnamed")
        
        try:
            if section_type == "static":
                passed, detail = self._run_static_check(case, stage_name)
            elif section_type == "logic":
                passed, detail = self._run_logic_test(case, stage_name)
            elif section_type == "data":
                passed, detail = self._run_data_check(case)
            elif section_type == "bridge":
                passed, detail = self._run_bridge_check(case)
            elif section_type == "syntax":
                passed, detail = self._run_syntax_check(case, stage_name)
            else:
                passed, detail = False, "unknown test type"
        except Exception as e:
            passed, detail = False, str(e)
        
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"    {symbol} [{status}] {name}")
        if not passed:
            print(f"           {detail}")
        
        self.results["passed" if passed else "failed"] += 1
        self.results["cases"].append({
            "stage": stage_name,
            "type": section_type,
            "name": name,
            "status": status,
            "detail": detail
        })
    
    # ── Static Checks ──────────────────────────────────────────────────────
    
    def _run_static_check(self, case, stage_name):
        check = case.get("check", "")
        expect = case.get("expect", "")
        stage_num = stage_name.replace("stage", "")
        html_path = os.path.join(self.project, f"stage{stage_num}_browser", "index.html")
        
        if not os.path.exists(html_path):
            return False, f"file not found: {html_path}"
        
        with open(html_path) as f:
            content = f.read()
        
        if check == "function_exists":
            fn = case.get("fn", "")
            found = f"function {fn}" in content or f"async function {fn}" in content
            if found:
                return True, f"function {fn} found"
            return False, f"function {fn} NOT found in {os.path.basename(html_path)}"
        
        elif check == "string_exists":
            expect_val = case.get("expect", "")
            found = expect_val in content
            if found:
                return True, f"'{expect_val[:60]}' found"
            return False, f"'{expect_val[:60]}' NOT found"
        
        elif check == "regex_exists":
            pattern = case.get("expect", "")
            found = bool(re.search(pattern, content))
            if found:
                return True, f"pattern '{pattern[:60]}' found"
            return False, f"pattern '{pattern[:60]}' NOT found"
        
        elif check == "import_exists":
            shared_file = case.get("file", "")
            found = shared_file in content
            if found:
                return True, f"imports {shared_file}"
            return False, f"does NOT import {shared_file}"
        
        elif check == "column_defined":
            col_name = case.get("expect", "")
            found = col_name in content
            if found:
                return True, f"column '{col_name}' defined"
            return False, f"column '{col_name}' NOT found"
        
        elif check == "db_table_exists":
            table_expr = case.get("expect", "")
            found = table_expr in content
            if found:
                return True, f"DB table {table_expr}"
            return False, f"DB table {table_expr} NOT found"
        
        return False, f"unknown static check: {check}"
    
    # ── Logic Tests ────────────────────────────────────────────────────────
    
    def _run_logic_test(self, case, stage_name):
        logic_code = case.get("logic", "")
        expect = case.get("expect", "")
        
        if not logic_code:
            return False, "no logic code provided"
        
        # Wrap logic in a test harness
        test_js = f"""
var passed = 0, failed = 0;
{logic_code}
if (failed > 0) process.exit(1);
"""
        
        result = subprocess.run(
            ["node", "-e", test_js],
            capture_output=True, text=True, timeout=15,
            cwd=self.project
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return True, output[:200] if output else "OK"
        else:
            error = (result.stderr or result.stdout).strip()
            return False, error[:200]
    
    # ── Data Checks ────────────────────────────────────────────────────────
    
    def _run_data_check(self, case):
        check = case.get("check", "")
        file_rel = case.get("file", "")
        file_path = os.path.join(self.project, file_rel)
        
        if not os.path.exists(file_path):
            return False, f"file not found: {file_rel}"
        
        if check == "csv_has_columns":
            expected_cols = [c.strip() for c in case.get("expect", "").split(",")]
            with open(file_path, newline='') as f:
                reader = csv.reader(f)
                headers = next(reader)
            for col in expected_cols:
                if col not in headers:
                    return False, f"missing column '{col}' in {file_rel}"
            return True, f"all {len(expected_cols)} columns present in {file_rel}"
        
        elif check == "csv_min_rows":
            min_rows = int(case.get("expect", "1"))
            with open(file_path, newline='') as f:
                count = sum(1 for _ in f) - 1  # minus header
            if count >= min_rows:
                return True, f"{count} rows (>= {min_rows}) in {file_rel}"
            return False, f"only {count} rows (< {min_rows}) in {file_rel}"
        
        return False, f"unknown data check: {check}"
    
    # ── Bridge Checks ──────────────────────────────────────────────────────
    
    def _run_bridge_check(self, case):
        check = case.get("check", "")
        stage_num = case.get("args", "")
        
        bridge_path = os.path.join(self.project, "shared", "stage-bridge.js")
        if not os.path.exists(bridge_path):
            return False, "bridge module not found"
        
        if check == "save_load_keys":
            # Verify the bridge key construction pattern exists
            with open(bridge_path) as f:
                bridge_content = f.read()
            # Check for the dynamic key construction pattern
            patterns_ok = []
            patterns_ok.append("PREFIX" in bridge_content)
            patterns_ok.append("stage" in bridge_content)
            patterns_ok.append("_to_" in bridge_content)
            patterns_ok.append("saveForNext" in bridge_content)
            patterns_ok.append("loadFromStage" in bridge_content)
            if all(patterns_ok):
                return True, "bridge key construction pattern verified"
            return False, "bridge key construction pattern incomplete" 
        
        return False, f"unknown bridge check: {check}"
    
    # ── Syntax Checks ──────────────────────────────────────────────────────
    
    def _run_syntax_check(self, case, stage_name):
        stage_num = stage_name.replace("stage", "")
        html_path = os.path.join(self.project, f"stage{stage_num}_browser", "index.html")
        
        if not os.path.exists(html_path):
            return False, f"file not found: {html_path}"
        
        with open(html_path) as f:
            content = f.read()
        
        scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
        big_scripts = [s for s in scripts if len(s) > 500]
        js_code = "\n".join(big_scripts)
        
        result = subprocess.run(
            ["node", "--check", "-"],
            input=js_code, capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            return True, "JS syntax valid"
        return False, result.stderr.strip()[:200]
    
    # ── Report ─────────────────────────────────────────────────────────────
    
    def _print_summary(self):
        r = self.results
        total = r["passed"] + r["failed"]
        print(f"\n{'═' * 60}")
        print(f"  TOTAL: {total}  |  PASS: {r['passed']}  |  FAIL: {r['failed']}")
        print(f"  PASS RATE: {r['passed']/total*100:.1f}%" if total else "  NO TESTS")
        print(f"{'═' * 60}")
    
    def _generate_report(self):
        r = self.results
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_path = os.path.join(REPORT_DIR, f"report_{ts}.md")
        json_path = os.path.join(REPORT_DIR, f"report_{ts}.json")
        latest = os.path.join(REPORT_DIR, "latest.md")
        
        with open(json_path, 'w') as f:
            json.dump(r, f, indent=2)
        
        with open(md_path, 'w') as f:
            f.write(f"# GPS Pricing Workbench — Test Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"| Total | Pass | Fail | Rate |\n")
            total = r["passed"] + r["failed"]
            rate = f"{r['passed']/total*100:.1f}%" if total else "N/A"
            f.write(f"| {total} | {r['passed']} | {r['failed']} | {rate} |\n\n")
            
            # Group by stage
            by_stage = {}
            for c in r["cases"]:
                s = c["stage"]
                if s not in by_stage: by_stage[s] = []
                by_stage[s].append(c)
            
            for stage, cases in sorted(by_stage.items()):
                f.write(f"## {stage}\n\n")
                f.write(f"| Status | Type | Test |\n")
                f.write(f"|--------|------|------|\n")
                for c in cases:
                    f.write(f"| {c['status']} | {c['type']} | {c['name']} |\n")
                f.write("\n")
        
        # Symlink latest
        if os.path.exists(latest):
            os.remove(latest)
        os.symlink(os.path.basename(md_path), latest)
        
        print(f"\n  Report: {md_path}")
        print(f"  Latest: {latest}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", help="Filter by stage (3,4,5,6)")
    parser.add_argument("--type", choices=["static","logic","data","bridge","syntax"], help="Filter by test type")
    parser.add_argument("--report", default="md", help="Report format")
    args = parser.parse_args()
    
    runner = TestRunner()
    runner.run(stage=f"stage{args.stage}" if args.stage else None, test_type=args.type)
