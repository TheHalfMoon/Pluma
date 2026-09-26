# T05-06 evidence report — Automated long-horizon continuity soak

- **Plan contract:** `docs/canonical/FLAKE_CANONICAL_BUILD_PLAN.md` §25/§28, task `T05-06`,
  under the Founder replacement contract
  (`docs/canonical/FOUNDER_NO_HUMAN_QUALIFICATION_GATES_2026-09-16.md`: automated
  long-horizon continuity soak instead of the voluntary human adoption study).
- **Dependencies:** `T05-05` (COMPLETE).
- **Executor:** fresh CI runners per native profile (no developer-workstation state).
- **Reviewer identity and independence limits:** Self-reviewed. No second human reviewer.

## What this is not

No human participants, no voluntary use, no adoption, retention, preference, or market
evidence is claimed here — by Founder decision those questions are deferred, not answered.
Eight "lanes" are disposable nonsecret workstreams driven by a seeded deterministic script;
ten "workdays" are simulated op batches. Allowed claim after PASS: the bounded product loop
is technically qualified over a long horizon on the measured environments. Forbidden claim:
any user preference, effort, adoption, or demand statement.

## Scope

```text
docs/evidence/flake-v1/T05-06/checks/continuity_soak.py | new (seeded 8x10 soak + file-only independent verify)
.github/workflows/t05-06-continuity-soak.yml | new (workflow_dispatch-only matrix: windows/macos/ubuntu)
docs/evidence/flake-v1/T05-06/REPORT.md | new (this report)
```

No `src/`, `desktop/src-tauri/src/`, or `desktop/src/` change.

## Method

Per profile, the harness drives the real release `pluma` binary (every call a fresh process:
genuine restart/close/reopen boundaries) through sealed seeded schedules (seed `20260926`,
schedule SHA-256 recorded per lane): capture/type creates, a state-tracked action lifecycle
(only transitions `src/project.rs`'s own table allows), explicit owner decisions with
acceptance, file-evidence import/linking/recheck, per-day search, per-day resume (later
resumptions), per-day checkpoints, mid-lane derived-index deletion plus rebuild proof,
backup-run (independently verified) plus backup-restore plus read-back, and a final full
export plus import-full-restore roundtrip with read-back. Wall-clock, invocation counts, and
vault/export bytes are recorded per lane. The verify pass re-derives everything from vault
and export bytes via `tools/independent-verify/sqlite_reader.py` (chain verification plus
acknowledged-write accounting: every created object present with its kind), never from run
logs.

## Status

```text
T05-06_STATUS=IN_PROGRESS
T05-06_SOAK_WORKFLOW=.github/workflows/t05-06-continuity-soak.yml
T05-06_CI_RUN=PENDING (harness + workflow implemented in this change; no PASS claimed before it runs green on all three profiles and is independently checked)
```

`T05-07` remains not dependency-ready until this report records a genuinely green,
independently checked run.
