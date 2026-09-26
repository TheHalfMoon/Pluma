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

## Defects found and fixed by this task's own qualification (no gate weakened)

Two consecutive `workflow_dispatch` runs failed identically on all three profiles with two
distinct harness-only defects (no product code involved, no acceptance clause weakened):

1. Run
   [`36261349597`](https://github.com/TheHalfMoon/Pluma/actions/runs/36261349597): the
   harness asserted `"verified=True"` in `backup-run` output, but the CLI prints Rust's
   `verified=true` (lowercase). Every lane aborted at the backup step after 35–59 commands
   of successful soak. Fixed to a case-insensitive match.
2. Run
   [`36266195822`](https://github.com/TheHalfMoon/Pluma/actions/runs/36266195822):
   `must()` appends `--vault <lane-vault>` to every call, so `import-full-restore`
   received two `--vault` values and the lane vault won as destination (`import destination
   already exists`). Fixed with `must_raw()`/`run_raw()` (no appended flag) for
   `import-full-restore` and `backup-restore`, whose destinations are their own flags.

## Addendum: continuity soak qualification PASS (2026-09-26, CI run 36269118724)

`.github/workflows/t05-06-continuity-soak.yml` ran on `main` at
`50eadc5db49e128035523db61b326d26fe82ec77` (post-fix): CI run
[`36269118724`](https://github.com/TheHalfMoon/Pluma/actions/runs/36269118724), conclusion
`success` on all three profiles. Independently confirmed from the downloaded per-profile
`continuity-soak.json` artifacts (seed `20260926`, `passed: true`, `failures: []` on every
profile — not merely the green checkmark):

- **8/8 lanes complete sealed schedules** per profile (schedule SHA-256 recorded per lane;
  identical schedules across profiles — determinism holds cross-platform).
- **Active days 6–9 per lane** (minimum 6 met); **resumptions 5–8 per lane** (minimum 3
  met); every lane covers capture (12–18), evidence (1–3), decision (6–9),
  action (3–4), resume, and export paths.
- **Restart boundaries genuine**: 70–102 fresh CLI processes per lane; per-lane wall-clock
  0.3–1.4 s and vault bytes (110–131 KiB) preserved as resource measurements.
- **Derived-state rebuild proven per lane** (index deleted mid-lane, `fts-update`
  rebuilt, loop continued); **backup independently verified plus restore-read per lane**;
  **full export plus import-full-restore roundtrip with read-back per lane**
  (export 47–72 KiB).
- **Independent file-only verification clean per lane**: head-hash chain verified over
  44–67 commands, 27–41 current objects, every acknowledged creation present with its
  kind (zero data loss, zero history loss, zero disclosure surface — the soak exchanges
  no packages/proposals by design).
- **Cross-platform agreement**: identical lane schedules, identical vault byte counts,
  and identical chain command counts on windows/macOS/ubuntu; export byte counts differ
  trivially by platform (path separators), with identical semantic counts.

```text
T05-06_STATUS=COMPLETE
T05-06_CI_RUN=36269118724
```

`T05-07` is now dependency-ready. No adoption, retention, preference, or demand claim is
made — the Founder decision defers those questions.
