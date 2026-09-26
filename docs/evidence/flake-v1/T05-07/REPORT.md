# T05-07 evidence report — Audit the exact release against R01-R12

- **Plan contract:** `docs/canonical/FLAKE_CANONICAL_BUILD_PLAN.md` §25/§28, task `T05-07`
- **Dependencies:** `T05-06` (COMPLETE)
- **Executor:** CI (`ubuntu-latest`; the audit is platform-independent and every
  per-profile claim it cites was already recorded by its owning task's native run)
- **Reviewer identity and independence limits:** Self-reviewed. No second human reviewer.

## Objective (plan §25)

Determine release readiness from complete evidence rather than completion checkboxes: map
every R01-R12 requirement to the exact tested revision/artifact, verify all raw manifests
and failures/limitations, inspect the final source/security/dependency diff since
qualification, rerun affected checks for any change, confirm no forbidden capabilities or
paid-model/core-network dependency, verify the reporting route, notices, support profiles,
and recovery instructions. Do not upload or publish.

## Scope

```text
docs/evidence/flake-v1/T05-07/checks/release_audit.py | new (docs/bundle/closure/notices/runtime/SBOM/drift/traceability)
.github/workflows/t05-07-release-audit.yml | new (workflow_dispatch-only: fresh scans + audit + gh-API run re-verification)
docs/evidence/flake-v1/T05-07/REPORT.md | new (this report)
```

No `src/`, `desktop/src-tauri/src/`, or `desktop/src/` change.

## R01–R12 mapping (verdicts PENDING until the audit workflow runs green)

| Gate | Requirement | Evidence (exact) | Verdict |
|---|---|---|---|
| R01 | Canonical atomicity/history/idempotency; D1–D6 all profiles | T01-01..T01-04, T05-02 (38 VM/process cycles), T05-05 repro, T05-06 soak chains | PENDING |
| R02 | Source/time/conflict/override, zero hidden disallowed state | T03-01..T03-03 | PENDING |
| R03 | Complete export/import/legacy migration + independent recovery | T02-05..T02-07, T05-01 M/L timings, T05-02 recovery, T05-05 migration repeat + reconstruction, T05-06 backup/restore | PENDING |
| R04 | Default-deny disclosure/proposal/security + current supply-chain review | T03-04..T03-06, T05-04 advisory refresh, fresh T05-07 scans | PENDING |
| R05 | Model/account/network-free end-to-end loop | T04-01 network-denied, T05-03/05 no-network-on-launch, T04-06 bundle surface | PENDING |
| R06 | All hard performance/bounds gates | section27-performance + m-scale-performance CI (green every PR), T05-01 M/L, T05-02 matrix | PENDING |
| R07 | Supported version refusal + migration fixtures | T05-01, tests/fixtures (format-compat, migration), refusal tests | PENDING |
| R08 | Clean native offline install/update/uninstall + retained data | T05-03/04/05 install_test all profiles, direct-distribution quals, DOWNLOAD/USER_GUIDE | PENDING |
| R09 | Licenses/notices/rights/SBOM/signatures + reproducibility | T05-04 (LICENSE/NOTICE/361/SBOM/GPG/attestations), T05-05 repro + PE isolation | PENDING |
| R10 | CLI/desktop/protocol/format/recovery/security reporting docs | USER_GUIDE, RELEASE_VERIFICATION, DOWNLOAD, CODE_SIGNING_POLICY, formats ×6, `pluma license`, issues route | PENDING |
| R11 | Automated continuity + long-horizon soak (amended; no human claim) | T03-08 automated continuity, T05-06 soak 8×10 (run 36269118724) | PENDING |
| R12 | Independent reproduction + no unresolved release-blocking regression | T05-05 (run 36254592422), all-PR CI green | PENDING |

## Status

```text
T05-07_STATUS=IN_PROGRESS
T05-07_AUDIT_WORKFLOW=.github/workflows/t05-07-release-audit.yml
T05-07_CI_RUN=PENDING (audit implemented in this change; no PASS claimed before it runs green and is independently checked)
```

`T05-08` remains not dependency-ready until every gate above reads PASS with exact linked
evidence and no unresolved blocking unknown.

## Addendum: release audit qualification PASS (2026-09-26, CI run 36274506387)

`.github/workflows/t05-07-release-audit.yml` ran on `main` at
`7895fb69db6bedc2c35e7153a966c9b9f2aff112`: CI run
[`36274506387`](https://github.com/TheHalfMoon/Pluma/actions/runs/36274506387), conclusion
`success`. Independently confirmed from the downloaded evidence artifact (not merely the
green checkmark) — `dist/t05-07/release-audit.json` reads `"passed": true` with all eight
check groups true:

- **required_docs:** all 16 release/format/license documents present and non-empty.
- **bundle_network_surface:** 1 built JS file, 0 violations (same inert baseline T04-01
  through T04-06 qualified — Vite's same-origin polyfill only).
- **root_closure:** 52 locked packages, 0 network/model/account/sync deny hits.
- **notices:** `Cargo.toml` declares Apache-2.0; THIRD-PARTY-LICENSES.md complete
  (Unicode + MPL families attributed).
- **license_runtime:** release `pluma license` exits 0 and names Apache-2.0, the
  `github.com/TheHalfMoon/Pluma` source, the issues support route, and offline operation.
- **sboms:** 6 current CycloneDX SBOMs generated for this exact revision.
- **product_code_drift:** zero commits touching `src/`, desktop sources, `tauri.conf.json`,
  or any lockfile since `d9fed64` (the last product-code change, PR #118 rename) — no
  affected-check rerun required beyond the fresh scans in this run.
- **traceability:** all 36 task REPORTs exist; all 13 CI run IDs named by CURRENT
  re-verified `success` via the gh API in the same run (`run-conclusions.txt`).
- **Fresh scans:** root `cargo audit` exit 0 with empty findings stdout (0 findings —
  cargo-audit emits findings on stdout and fetch progress on stderr); desktop `cargo
  audit` exit 0 with the same 7 non-blocking unmaintained/unsound warnings T05-04 already
  recorded (RUSTSEC-2024-0370/0081/0075/0080/0098/0100/0429 — 0 vulnerabilities, no new
  advisory since); `npm audit` reports `found 0 vulnerabilities`.

## Final R01–R12 verdicts

| Gate | Verdict | Exact linked evidence |
|---|---|---|
| R01 | PASS | T01-01..T01-04 REPORTs; T05-02 (38 cycles, zero loss); T05-05 repro; T05-06 soak chains (run 36269118724) |
| R02 | PASS | T03-01..T03-03 REPORTs |
| R03 | PASS | T02-05..T02-07; T05-01 M/L timings; T05-02 recovery; T05-05 migration repeat + reconstruction (run 36254592422); T05-06 backup/restore |
| R04 | PASS | T03-04..T03-06; T05-04 advisory refresh; fresh T05-07 scans (run 36274506387, 0 vulns) |
| R05 | PASS | T04-01 network-denied; T05-03/05 no-network-on-launch; T04-06 bundle surface; T05-07 root-closure + bundle re-check |
| R06 | PASS | section27-performance + m-scale-performance CI green on every merged PR including this cycle; T05-01 M/L; T05-02 matrix |
| R07 | PASS | T05-01; tests/fixtures (format-compat, migration); refusal tests in suite |
| R08 | PASS | T05-03/04/05 install_test on all native profiles; Windows/macOS direct-distribution install quals (runs 36243789672, 35514419522); DOWNLOAD/USER_GUIDE instructions; uninstall retains vaults |
| R09 | PASS | T05-04 (LICENSE/NOTICE/361 components/6 SBOMs/GPG `F77980…87FE22`/attestations); Linux + macOS + Windows direct-web quals; T05-05 repro + PE isolation |
| R10 | PASS | USER_GUIDE, RELEASE_VERIFICATION, DOWNLOAD, CODE_SIGNING_POLICY, formats ×6, `pluma license` runtime facts (re-proven run 36274506387), issues support route |
| R11 | PASS | Amended contract (no human claim): T03-08 automated continuity; T05-06 soak 8×10 (run 36269118724) |
| R12 | PASS | T05-05 independent reproduction (run 36254592422); full required CI green on every merged PR; zero open release-blocking regressions |

No unresolved blocking unknown remains. The local candidate set (CLI archives, desktop
installer bundles per profile, SBOMs, manifests, signatures, attestations) is present and
verified as recorded by the owning runs above.

```text
T05-07_STATUS=COMPLETE
T05-07_CI_RUN=36274506387
```

`T05-08` is now dependency-ready. Actual public publication remains separately authorized
and is not required for completion.
