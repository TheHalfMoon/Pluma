# T05-08 evidence report — Verified project completion and release baseline

- **Plan contract:** `docs/canonical/FLAKE_CANONICAL_BUILD_PLAN.md` §25/§28/§37, task `T05-08`
- **Dependencies:** `T05-07` (COMPLETE, R01–R12 all PASS)
- **Executor:** repository session against live GitHub truth (evidence-only closeout; no
  product-code change, no new feature tests, no upload, no publication)
- **Reviewer identity and independence limits:** Self-reviewed. No second human reviewer.

## Objective (plan §25)

Verify the predecessor and all phase gates; freeze the tested source/release digests; write
the evidence-only completion record. Set `PROJECT_COMPLETE=YES` only under section 37.
Record unsupported systems, residual honest limits, and deferred scope. No source change
after qualification inside this task, no automatic post-completion feature or publication.

## 1. Predecessor and phase gates

All 38 task IDs are COMPLETE with exact evidence (`docs/evidence/flake-v1/<ID>/REPORT.md`
verified present for all 38, including this report; statuses per `specs/CURRENT.md`):

- P00 intake/plan: T00-01 COMPLETE
- P01 corrective convergence + format-2 path: T00-02, T01-01..T01-07 COMPLETE (P01 CLOSED)
- P02 CLI project loop + portable reconstruction: T02-01..T02-07 COMPLETE
- P03 scoped items/exact receipts/visible evidence: T03-01..T03-08 COMPLETE (P03 CLOSED)
- P04 thin desktop + native accessibility + recovery/export: T04-01..T04-06 COMPLETE
  (P04 CLOSED)
- P05 release/disribution/qualification: T05-01, T05-02, T05-03, T05-04, T05-05, T05-06,
  T05-07 COMPLETE; this task closes T05-08, completing P05 and every section 36 gate at
  the exact release revision.

R01–R12: all PASS per `docs/evidence/flake-v1/T05-07/REPORT.md` (audit run
36274506387). Six phase gates satisfied by task completion above; no missing platform, no
inconclusive value trial (automated contracts per Founder amendments).

## 2. Frozen digests

Audited `main` (pre-closeout, carrying every qualification above):

```text
AUDITED_MAIN=19d3a953186cfdcb7edcf05cfc84d4700dd8faa5
AUDITED_TREE=08fc0d445cd0443755eef4b8b723b3873d7fd6d8
```

This closeout adds only `docs/evidence/flake-v1/T05-08/REPORT.md` (this file) and the
`specs/CURRENT.md` completion pointer — no `src/`, desktop, workflow, script, or lockfile
change, so no re-qualification is triggered (the T05-07 product-code drift gate,
baseline `d9fed64`, remains clean by construction). The merge commit of this closeout PR
is the canonical completion commit; its tree is recorded in `specs/CURRENT.md` after merge
verification. Worktree verified clean at closeout (`git status` empty apart from this
change); no unrelated work is mixed in (open Fehrest V2 proposal PRs #2/#40 remain
explicitly out of scope; `SPEC_003_AUTO_ACTIVATION=PROHIBITED`).

Release artifact identities (exact, as recorded by the owning runs — never retyped):

```text
HISTORICAL_RC_TAG=v0.0.1-phase-t-rc.1 (preserved, prerelease, Windows-only, Flake-branded)
Flake_0.0.1-phase-t_x64-setup.exe=83c077a3b4c39bf0751a193c0c56e554597339cc6f868918f29a61238d8a0b44
flake-0.0.1-phase-t-windows-x86_64.zip=1b8a66d789bb461a6d35333859d9c0b3a3def1c57f0b0ffd79441f5b978c8f3e
WINDOWS_DIRECT_WEB (run 36243789672, Pluma-branded):
Pluma_0.0.1-phase-t_x64-setup.exe=09c5d0d161603ac607e5d3695a9569e0bec7badd3d2a71a07995d64de0faa41b
pluma-0.0.1-phase-t-windows-x86_64.zip=6767273e02eaa34918ba11119fb41bf7064923c280f5ab4b274fcb4a35d30fe2
pluma-0.0.1-phase-t-windows-x86_64.sha256=54dc502ca7dfee89037f3ef0a5fa80079449140d6d7ad8362a79791838e416e5
MACOS_DIRECT (run 35514419522):
Flake_0.0.1-phase-t_aarch64.dmg@sha256:310c035d23e6b88f67b6b6ff51e195696970f2886ca9ba43381be420f5141afc
T05-05_REPRO (ubuntu/macOS pluma, byte-identical across runs):
ubuntu pluma=a020ee9975a843f05c31d0a07906107362bb115d363e5c27196dd51b03c05e05
macos pluma=afad9c46ac79c683396f87280974385e3cce29e9734b6f3ad19c3705caafab59
GPG_IDENTITY=F779807C73F29F4DB1E7DC9F78F7D4B92287FE22 (Flake Release Signing)
CANONICAL_PLAN_SHA256=b555f83ff12882ae6f55f90bbeaa411de52b84661a7f3953350cbfc6bd789fb2
```

## 3. Distribution and trust states (final)

```text
WEBSITE_FIRST_DIRECT_DISTRIBUTION=YES
MICROSOFT_STORE_DISTRIBUTION=NO
MAC_APP_STORE_DISTRIBUTION=NO
MANDATORY_APP_STORE_DISTRIBUTION=NO
FOUNDER_ZERO_COST_DISTRIBUTION_REQUIRED=YES
WINDOWS_DIRECT_WEB_DISTRIBUTION=PASS
WINDOWS_AUTHENTICODE_TRUST=NOT_AVAILABLE
WINDOWS_AUTHENTICODE_TRUST_CLAIMED=NO
WINDOWS_SMARTSCREEN_WARNING=EXPECTED_AND_DISCLOSED
MACOS_DISTRIBUTION_MODE=DIRECT_WEBSITE
MACOS_DEVELOPER_ID_REQUIRED=NO
MACOS_NOTARIZATION_REQUIRED=NO
MACOS_GATEKEEPER_TRUST=NOT_CLAIMED
MACOS_APPLE_PLATFORM_TRUST=NOT_CLAIMED
LINUX_GPG_RELEASE_SIGNING=PASS
```

Public download locations: source `https://github.com/TheHalfMoon/Pluma`, releases
`https://github.com/TheHalfMoon/Pluma/releases`, landing `docs/release/DOWNLOAD.md`,
verification `docs/release/RELEASE_VERIFICATION.md`, policy
`docs/release/CODE_SIGNING_POLICY.md`. No final production release is published — actual
public publication is separately Founder-authorized and is not required for completion;
the historical `v0.0.1-phase-t-rc.1` prerelease is preserved untouched.

## 4. Install / launch / update / rollback / uninstall evidence

- Clean install/launch/reinstall/uninstall with vault retention on all native profiles:
  T05-03 (`install_test.sh` matrix), T05-04 Windows/macOS direct-distribution
  reconfirmations (runs 36243789672, 35514419522), T05-05 per-profile install
  qualification (run 36254592422).
- Update model: manual verified-package replacement (no auto-updater by design);
  reinstall-over-existing qualified as the update stand-in; format upgrades require
  explicit migration-to-new-root after backup (`docs/release/USER_GUIDE.md` §6–§7).
- Rollback: retained older verified binaries refuse (never misinterpret) newer-format
  vaults; backups restore to fresh roots without touching originals (T05-06 per-lane
  backup/restore proofs).
- Uninstall removes application files only and reports vault retention (no silent vault
  destruction).

## 5. Residual honest limits (not blockers)

- Windows builds are unsigned: SmartScreen/reputation warnings expected and disclosed.
- macOS builds are unnotarized: per-app Gatekeeper override required, never Apple trust.
- No auto-updater; updates are manual verified downloads.
- No human usability/adoption/retention/preference evidence by Founder decision (deferred,
  never claimed).
- Desktop `cargo audit` keeps 7 non-blocking unmaintained/unsound warnings
  (RUSTSEC-2024-0370/0081/0075/0080/0098/0100/0429), 0 vulnerabilities — upstream Tauri/GTK
  stack, outside this task's scope.
- Windows PE binaries carry per-link timestamps/PDB GUIDs (isolated, remainder
  bit-identical — `scripts/release/pe_reproducibility.py`).
- Performance gates measured at the recorded scales/hosts (M: 10k records; L: 100k
  import 217.54 s); broader hardware is unmeasured, not claimed.
- Qualified profiles only (below); anything else is untested, not supported-by-evidence.

## 6. Supported and unsupported systems

Supported (natively qualified): Windows x86_64 (current-user NSIS install), macOS aarch64
14.0+ (`.dmg`/`.app` copy), Linux x86_64 (`.deb`/CLI archive, GPG-signed). Unsupported /
unproven: 32-bit platforms, Windows ARM64, macOS x86_64 and macOS < 14, non-Debian Linux
packaging (CLI archive is portable), mobile OSes, and any broader market/agent-performance
claim (explicitly unproven per §37).

## 7. Deferred scope (not hidden completion tasks)

Plan §38 post-completion deferrals stand (cloud sync, collaboration, auth/SSO, mobile,
rich editors, graph/vector/model runtimes, plugins, remote execution, auto-update, and the
rest named there). Future trust improvements (not v1 blockers):
`SIGNPATH_FOUNDATION_REAPPLY_AFTER_PUBLIC_ADOPTION=YES`,
`OSSIGN_REAPPLY_WHEN_ELIGIBLE=YES`. No paid certificate, membership, hosting, CI,
storage, API, model, Store registration, or distribution platform was introduced or is
required — founder cost for v1 is zero.

## 8. Completion declaration

Under plan §37 — all 38 tasks evidence-complete, six phase gates satisfied, R01–R12 PASS,
the qualified release-candidate set present and verified, the tested source/tree frozen
above, all retained workflows green with no network/account/model/remote-repository
dependence in the product, and zero unresolved acknowledged data loss, false recovery,
disallowed disclosure, missing provenance, silent mutation, missing rights, or unexplained
build divergence:

```text
PROJECT_COMPLETE=YES
EXTERNAL_BLOCKERS=NONE
```

Zero fabricated claims. Zero unresolved canonical blockers. Historical evidence (4246f6d,
sealed R1, T03-07 seals, every failed experiment) preserved unrewritten.
