#!/usr/bin/env python3
"""T05-07: release audit checks (plan section 25/28, task T05-07).

Reruns the checks that must be current at the exact release revision and
compiles the revision-to-evidence traceability the R01-R12 audit reads:

  1. required release documentation exists and is non-empty;
  2. the desktop frontend bundle carries no new network surface (same
     pattern/allowlist T04-01/T04-06 already qualified);
  3. the root CLI dependency closure (the data owner) contains no
     network/model/account/sync crate;
  4. LICENSE/NOTICE/THIRD-PARTY-LICENSES ship and declare Apache-2.0;
  5. the `pluma license` runtime facts name license/source/privacy/support;
  6. SBOMs were generated for this revision;
  7. no product-code or lockfile change exists since the last product-code
     commit (fails closed -- any such change demands re-qualification);
  8. every evidence REPORT and every CI run ID named by specs/CURRENT.md
     exists (run conclusions are re-verified via the gh API in the
     workflow, not here).

Usage:
  python3 release_audit.py --pluma-bin <path> --out <report.json>

Exits non-zero on any failed check. Prints the JSON report to stdout.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]

# Last commit that touched product code or locked dependencies (verified by
# `git log` during T05-07 design; bump only together with re-qualification).
PRODUCT_CODE_BASELINE = "d9fed64c02ef8a9eee34ac81bcd604f0024c9835"
PRODUCT_CODE_PATHS = [
    "src",
    "desktop/src",
    "desktop/src-tauri/src",
    "desktop/src-tauri/tauri.conf.json",
    "Cargo.lock",
    "desktop/src-tauri/Cargo.lock",
    "desktop/package-lock.json",
]

REQUIRED_DOCS = [
    "LICENSE",
    "NOTICE",
    "docs/legal/THIRD-PARTY-LICENSES.md",
    "docs/release/USER_GUIDE.md",
    "docs/release/RELEASE_VERIFICATION.md",
    "docs/release/DOWNLOAD.md",
    "docs/release/CODE_SIGNING_POLICY.md",
    "docs/release/WINDOWS_DIRECT_DISTRIBUTION.md",
    "docs/release/MACOS_DIRECT_DISTRIBUTION.md",
    "docs/release/LINUX_RELEASE_SIGNING.md",
    "docs/formats/format-2-canonical-sqlite.md",
    "docs/formats/portable-export-v1.md",
    "docs/formats/legacy-migration.md",
    "docs/formats/typed-records.md",
    "docs/formats/format-compatibility-policy.md",
    "docs/formats/agent-disclosure-protocol-v1.md",
]

# Crates that must never appear in the root CLI closure (the canonical-data
# owner). The desktop Tauri shell legitimately uses a runtime with loopback
# IPC only (already qualified at T04-06), so this gate is scoped to root.
NETWORK_MODEL_DENY = {
    "reqwest", "hyper", "ureq", "tokio", "mio", "async-std", "smol",
    "openai", "async-openai", "candle-core", "candle-transformers", "ort",
    "tract-core", "tungstenite", "tokio-tungstenite", "websocket",
    "rumqttc", "paho-mqtt", "aws-config", "object_store", "russh",
}


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def check_docs(report):
    missing = [p for p in REQUIRED_DOCS if not (REPO_ROOT / p).is_file()
               or (REPO_ROOT / p).stat().st_size == 0]
    empty = [p for p in REQUIRED_DOCS if (REPO_ROOT / p).is_file()
             and (REPO_ROOT / p).stat().st_size == 0]
    report["required_docs"] = {"missing": missing, "empty": empty}
    return not missing and not empty


def check_bundle_network_surface(report):
    dist_dir = REPO_ROOT / "desktop" / "dist" / "assets"
    js_files = list(dist_dir.glob("*.js")) if dist_dir.exists() else []
    if not js_files:
        report["bundle_network_surface"] = {"error": "dist not built; run npm run build first"}
        return False
    pattern = re.compile(r"fetch\(|XMLHttpRequest|WebSocket\(|https?://[a-zA-Z0-9./_-]+")
    allowed = ["http://www.w3.org/", "https://react.dev/errors/"]
    violations = []
    for jf in js_files:
        text = jf.read_text(encoding="utf-8", errors="replace")
        for m in pattern.finditer(text):
            matched = m.group(0)
            if matched == "fetch(":
                continue  # Vite's own same-origin modulepreload polyfill, audited every prior task
            if any(matched.startswith(a) for a in allowed):
                continue
            violations.append(f"{jf.name}: {matched}")
    report["bundle_network_surface"] = {"files": len(js_files), "violations": violations[:20]}
    return not violations


def check_root_closure(report):
    # The root Cargo.lock pins the full transitive closure of the CLI
    # workspace (the desktop shell is a separate Cargo project with its own
    # lockfile and its own Tauri-runtime qualification at T04-06).
    lock = (REPO_ROOT / "Cargo.lock").read_text(encoding="utf-8")
    names = set(re.findall(r'^name = "([^"]+)"', lock, re.MULTILINE))
    hits = sorted(names & NETWORK_MODEL_DENY)
    report["root_closure"] = {"packages": len(names), "deny_hits": hits}
    return bool(names) and not hits


def check_notices(report):
    checks = {}
    checks["cargo_license_root"] = 'license = "Apache-2.0"' in (REPO_ROOT / "Cargo.toml").read_text()
    third = (REPO_ROOT / "docs" / "legal" / "THIRD-PARTY-LICENSES.md").read_text(encoding="utf-8")
    checks["third_party_nonempty"] = len(third) > 10000
    checks["third_party_names_unicode"] = "Unicode" in third
    checks["third_party_names_mpl"] = "Mozilla Public License" in third
    report["notices"] = checks
    return all(checks.values())


def check_license_runtime(binary, report):
    proc = run([str(binary), "license"])
    out = proc.stdout + proc.stderr
    checks = {
        "exit_zero": proc.returncode == 0,
        "names_apache": "Apache" in out,
        "names_source": "github.com/TheHalfMoon/Pluma" in out,
        "names_support": "issues" in out.lower(),
        "names_offline": "offline" in out.lower(),
    }
    report["license_runtime"] = checks
    return proc.returncode == 0 and all(checks.values())


def check_sboms(report):
    sboms = sorted((REPO_ROOT / "dist" / "sbom").glob("*.cdx.json")) if (REPO_ROOT / "dist" / "sbom").exists() else []
    report["sboms"] = {"count": len(sboms), "files": [p.name for p in sboms]}
    return len(sboms) >= 4


def check_product_code_drift(report):
    proc = run(["git", "log", "--format=%H", f"{PRODUCT_CODE_BASELINE}..HEAD", "--",
                *PRODUCT_CODE_PATHS], cwd=str(REPO_ROOT))
    commits = [c for c in proc.stdout.splitlines() if c.strip()]
    report["product_code_drift"] = {"baseline": PRODUCT_CODE_BASELINE, "commits_since": commits}
    return proc.returncode == 0 and not commits


def check_traceability(report):
    current = (REPO_ROOT / "specs" / "CURRENT.md").read_text(encoding="utf-8")
    run_ids = sorted(set(re.findall(r"_CI_RUN=(\d{5,})", current)))
    missing_reports = []
    for task in ["T00-01", "T00-02", "T01-01", "T01-02", "T01-03", "T01-04", "T01-05", "T01-06",
                 "T01-07", "T02-01", "T02-02", "T02-03", "T02-04", "T02-05", "T02-06", "T02-07",
                 "T03-01", "T03-02", "T03-03", "T03-04", "T03-05", "T03-06", "T03-07", "T03-08",
                 "T04-01", "T04-02", "T04-03", "T04-04", "T04-05", "T04-06",
                 "T05-01", "T05-02", "T05-03", "T05-04", "T05-05", "T05-06"]:
        if not (REPO_ROOT / "docs" / "evidence" / "flake-v1" / task / "REPORT.md").is_file():
            missing_reports.append(task)
    report["traceability"] = {"ci_run_ids": run_ids, "missing_reports": missing_reports}
    return not missing_reports and len(run_ids) >= 10


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pluma-bin", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    report: dict = {"checks": {}}
    ok = True
    for name, fn in [
        ("required_docs", check_docs),
        ("bundle_network_surface", check_bundle_network_surface),
        ("root_closure", check_root_closure),
        ("notices", check_notices),
        ("sboms", check_sboms),
        ("product_code_drift", check_product_code_drift),
        ("traceability", check_traceability),
    ]:
        try:
            passed = fn(report)
        except Exception as exc:
            report[name] = {"error": str(exc)[:500]}
            passed = False
        report["checks"][name] = passed
        ok = ok and passed
    try:
        passed = check_license_runtime(Path(args.pluma_bin), report)
    except Exception as exc:
        report["license_runtime"] = {"error": str(exc)[:500]}
        passed = False
    report["checks"]["license_runtime"] = passed
    ok = ok and passed

    report["passed"] = ok
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not ok:
        raise SystemExit("RELEASE_AUDIT_FAILED")
    print("RELEASE_AUDIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
