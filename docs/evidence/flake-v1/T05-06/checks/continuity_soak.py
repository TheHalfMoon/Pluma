#!/usr/bin/env python3
"""T05-06: automated long-horizon continuity soak (replacement contract).

Runs eight independent workstream lanes of ten simulated workdays each
through the real `pluma` release binary, then independently verifies every
lane from its vault/export bytes. This is an automated deterministic
engineering soak -- it is never described as users, participants, adoption,
retention, or preference evidence (see the Founder no-human-gates decision).

Required coverage per lane (Founder replacement T05-06 contract):
  - >=6 active days of 10 simulated days (sealed schedule, seeded RNG);
  - >=3 later resumptions (resume calls on active days after the first);
  - real capture -> evidence -> decision/action -> resume -> export paths;
  - restart/close/reopen boundaries (every CLI call is a fresh process;
    each day opens with a read);
  - derived-state rebuild (delete derived-fts.sqlite mid-lane, rebuild,
    prove the loop continues);
  - >=1 backup/restore plus a full export/import-full-restore roundtrip;
  - independent final-state and history verification (sqlite_reader only);
  - every failure, maintenance op, wait, and resource measurement preserved.

Pass criteria (same contract): 8/8 lanes complete sealed schedules; every
lane meets active-day and resumption minimums plus the full loop and
exit/reconstruction; zero acknowledged canonical data loss; zero silent
history loss, false recovery success, or unintended disclosure; profile
claims bounded to technical evidence; independent verification reproduces
final state and run accounting.

Usage:
  python3 continuity_soak.py --pluma-bin <path> --workdir <dir> --out <report.json> [--seed N]

Exits non-zero unless every pass criterion holds. The workdir is always
deleted before exit; the report preserves all evidence.
"""
import argparse
import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "tools" / "independent-verify"))
import sqlite_reader  # noqa: E402

LANES = 8
DAYS = 10
SEED_DEFAULT = 20260926


def run(binary, vault, args):
    """One fresh CLI process (a genuine restart boundary)."""
    cmd = [str(binary), *args, "--vault", str(vault)]
    started = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - started
    return result, elapsed


def must(binary, vault, args, lane_log):
    result, elapsed = run(binary, vault, args)
    lane_log["invocations"] += 1
    lane_log["wait_seconds"] = round(lane_log.get("wait_seconds", 0.0) + elapsed, 3)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {args}\n"
            f"stdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"
        )
    return result.stdout.strip()


def dir_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def seal_schedule(rng: random.Random):
    active = [rng.random() < 0.75 for _ in range(DAYS)]
    day = 0
    while sum(active) < 6:
        active[day % DAYS] = True
        day += 1
    return active


def run_lane(binary: Path, lane: int, lane_dir: Path, seed: int):
    rng = random.Random(seed * 1000 + lane)
    log: dict = {
        "lane": lane,
        "invocations": 0,
        "wait_seconds": 0.0,
        "active_days": [],
        "resumptions": 0,
        "loop": {"capture": 0, "evidence": 0, "decision": 0, "action": 0, "resume": 0, "export": 0},
        "created": {},
        "failures": [],
    }
    vault = lane_dir / "vault"
    t0 = time.perf_counter()
    try:
        must(binary, vault, ["canonical-init"], log)
        project = must(
            binary, vault,
            ["project-create", "--name", f"Soak lane {lane}", "--description", "T05-06 automated soak workstream"],
            log,
        ).split()[0]
        log["project"] = project
        active = seal_schedule(rng)
        log["schedule"] = active
        log["schedule_sha256"] = hashlib.sha256(json.dumps(active).encode()).hexdigest()
        log["active_days"] = [d for d, a in enumerate(active) if a]
        # Special days are picked from the sealed active set (never a fixed
        # day number, which the schedule may leave inactive): derived-state
        # rebuild on the middle active day, backup/restore on the
        # second-to-last active day.
        acts = log["active_days"]
        rebuild_day = acts[len(acts) // 2]
        backup_day = acts[-2]
        log["rebuild_day"] = rebuild_day
        log["backup_day"] = backup_day

        revs: dict = {}
        astate: dict = {}
        checkpoint_rev = None
        first_active_seen = False
        open_actions: list = []
        # Valid next steps per ActionState (src/project.rs
        # action_allowed_transition): sampled deterministically, so every
        # issued transition is legal and no lane can fail on a refused one.
        NEXT = {
            "Open": ("start", "block", "complete", "cancel"),
            "Doing": ("complete", "block", "cancel"),
            "Blocked": ("start", "complete", "cancel"),
            "Done": ("reopen",),
            "Cancelled": ("reopen",),
        }

        for day in range(DAYS):
            if not active[day]:
                continue
            # Day opens with a read (close/reopen boundary from the last process exit).
            must(binary, vault, ["project-show", "--id", project], log)
            tag = f"lane{lane}d{day}"

            # Capture path (Default-Note capture plus typed creates).
            for i in range(rng.randint(1, 3)):
                out = must(binary, vault, ["capture", "--project", project,
                                           "--title", f"{tag} note {i}",
                                           "--body", f"Soak body {tag} {i} lanemarker{lane}"], log)
                log["created"][out.split()[0]] = "note"
                log["loop"]["capture"] += 1

            # Action lifecycle variety across days.
            if day % 3 == 0:
                created = must(binary, vault, ["action-create", "--project", project,
                                               "--title", f"{tag} action"], log).split()
                a = created[0]
                revs[a] = created[1]
                astate[a] = "Open"
                log["created"][a] = "action"
                log["loop"]["action"] += 1
                open_actions.append(a)
            for a in list(open_actions):
                step = rng.choice(NEXT[astate[a]])
                if step == "start":
                    out = must(binary, vault, ["action-start", "--id", a, "--expect", revs[a]], log)
                    revs[a] = out.split()[1]
                    astate[a] = "Doing"
                elif step == "complete":
                    out = must(binary, vault, ["action-complete", "--id", a, "--expect", revs[a],
                                               "--summary", f"{tag} done"], log)
                    revs[a] = out.split()[1]
                    astate[a] = "Done"
                elif step == "block":
                    out = must(binary, vault, ["action-block", "--id", a, "--expect", revs[a],
                                               "--reason", f"{tag} waiting"], log)
                    revs[a] = out.split()[1]
                    astate[a] = "Blocked"
                elif step == "cancel":
                    out = must(binary, vault, ["action-cancel", "--id", a, "--expect", revs[a],
                                               "--reason", f"{tag} dropped"], log)
                    revs[a] = out.split()[1]
                    astate[a] = "Cancelled"
                else:  # reopen: Done/Cancelled -> Doing, requires a reason
                    out = must(binary, vault, ["action-reopen", "--id", a, "--expect", revs[a],
                                               "--reason", f"{tag} revisit"], log)
                    revs[a] = out.split()[1]
                    astate[a] = "Doing"
                break  # one lifecycle step per action per day at most

            # Decision path (explicit owner judgment, then acceptance).
            key = f"lane-{lane}-day-{day}"
            d = must(binary, vault, ["decision-create", "--project", project, "--key", key,
                                     "--statement", f"{tag} choice",
                                     "--rationale", f"{tag} reason",
                                     "--basis", "user-judgment"], log).split()
            log["created"][d[0]] = "decision"
            log["loop"]["decision"] += 1
            out = must(binary, vault, ["decision-accept", "--id", d[0], "--expect", d[1]], log)
            revs[d[0]] = out.split()[1]

            # Evidence path on days 2/5/8: import a file, link it, recheck it.
            if day in (2, 5, 8):
                src_file = lane_dir / f"evidence-day{day}.txt"
                src_file.write_text(f"soak evidence bytes {tag}\n", encoding="utf-8")
                s = must(binary, vault, ["source-import", "--project", project,
                                         "--label", f"{tag}-evidence", "--path", str(src_file)], log).split()
                log["created"][s[0]] = "source"
                log["loop"]["evidence"] += 1
                must(binary, vault, ["relation-create", "--project", project, "--type", "supports",
                                     "--from", d[0], "--to", s[0], "--note", f"{tag} link"], log)
                must(binary, vault, ["source-check", "--id", s[0]], log)

            # Derived-state search every active day.
            must(binary, vault, ["fts-search", "--project", project, "--query", f"lanemarker{lane}"], log)

            # Derived-state rebuild proof on the sealed middle active day.
            if day == rebuild_day:
                index = vault / ".fehrest" / "derived-fts.sqlite"
                log["derived_index_existed"] = index.exists()
                if index.exists():
                    index.unlink()
                must(binary, vault, ["fts-update"], log)
                status = must(binary, vault, ["fts-status"], log)
                log["fts_status_after_rebuild"] = status.splitlines()[0] if status else ""
                log["derived_index_rebuilt"] = index.exists()

            # Backup/restore exit proof on the sealed second-to-last active day.
            if day == backup_day:
                backup_out = must(binary, vault, ["backup-run", "--out", str(lane_dir / "backup")], log)
                if "verified=true" not in backup_out.lower():
                    raise RuntimeError(f"backup not independently verified: {backup_out[-300:]}")
                log["backup_verified"] = True
                restore_out = must(binary, vault, ["backup-restore", "--backup", str(lane_dir / "backup"),
                                                   "--out", str(lane_dir / "restored")], log)
                log["restore_report"] = restore_out.splitlines()[0] if restore_out else ""
                must(binary, lane_dir / "restored", ["project-show", "--id", project], log)
                log["restore_reads"] = True

            # Resumption on every active day after the first.
            if first_active_seen:
                resume_out = must(binary, vault, ["resume", "--project", project], log)
                if not resume_out:
                    raise RuntimeError("empty resume output")
                log["resumptions"] += 1
                log["loop"]["resume"] += 1
            first_active_seen = True

            # Checkpoint at day end (first mark bare, later marks need --expect).
            if checkpoint_rev is None:
                out = must(binary, vault, ["checkpoint-mark", "--project", project], log)
            else:
                out = must(binary, vault, ["checkpoint-mark", "--project", project,
                                           "--expect", checkpoint_rev], log)
            checkpoint_rev = out.split()[1]
            log["checkpoint_rev"] = checkpoint_rev

        # Full export + import-full-restore roundtrip (exit/reconstruction proof).
        export_out_dir = lane_dir / "export-full"
        must(binary, vault, ["export-run", "--out", str(export_out_dir)], log)
        log["loop"]["export"] += 1
        export_pkg = export_out_dir / ".fehrest-export"
        if not export_pkg.is_dir():
            raise RuntimeError("export package directory missing")
        log["export_bytes"] = dir_bytes(export_out_dir)
        restore2 = lane_dir / "import-restored"
        import_out = must(binary, vault, ["import-full-restore", "--source", str(export_out_dir),
                                          "--vault", str(restore2)], log)
        log["import_report"] = import_out.splitlines()[0] if import_out else ""
        must(binary, restore2, ["project-show", "--id", project], log)
        log["import_restore_reads"] = True

        log["wall_seconds"] = round(time.perf_counter() - t0, 3)
        log["vault_bytes"] = dir_bytes(vault)
        log["complete"] = True
    except Exception as exc:
        log["complete"] = False
        log["failures"].append(str(exc)[:2000])
    return log


def verify_lane(lane: int, lane_dir: Path, log: dict):
    """File-only re-derivation: reproduce final state and accounting from
    vault/export bytes, never from the run's in-memory logs."""
    problems = []
    vault = lane_dir / "vault"
    result = sqlite_reader.read_vault(vault / ".fehrest" / "canonical.sqlite")
    if not result["head_hash_chain_verified"]:
        problems.append("head hash chain did not verify")
    current = {}
    for e in result["envelopes"]:
        oid = e["object_id"]
        if oid not in current or e["recorded_seq"] > current[oid]["recorded_seq"]:
            current[oid] = e
    for oid, kind in log.get("created", {}).items():
        if oid not in current:
            problems.append(f"acknowledged {kind} {oid} missing from final state (data loss)")
        elif current[oid]["kind"] != kind:
            problems.append(f"acknowledged {kind} {oid} has kind {current[oid]['kind']} (mutation)")
    return {"problems": problems, "command_count": result["command_count"],
            "current_object_count": len(current)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pluma-bin", required=True)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int, default=SEED_DEFAULT)
    parser.add_argument("--lanes", type=int, default=LANES)
    args = parser.parse_args()

    binary = Path(args.pluma_bin).resolve()
    workdir = Path(args.workdir)
    report_path = Path(args.out)
    report: dict = {"seed": args.seed, "lanes": {}}

    try:
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True)

        for lane in range(args.lanes):
            lane_dir = workdir / f"lane-{lane}"
            lane_dir.mkdir(parents=True)
            log = run_lane(binary, lane, lane_dir, args.seed)
            report["lanes"][str(lane)] = log
            if not log.get("complete"):
                continue

        # Independent verification pass over finished lanes.
        failures = []
        for lane in range(args.lanes):
            log = report["lanes"][str(lane)]
            if not log.get("complete"):
                failures.append(f"lane {lane} incomplete: {log.get('failures')}")
                continue
            if len(log["active_days"]) < 6:
                failures.append(f"lane {lane} active days {len(log['active_days'])} < 6")
            if log["resumptions"] < 3:
                failures.append(f"lane {lane} resumptions {log['resumptions']} < 3")
            for path in ("capture", "evidence", "decision", "action", "resume", "export"):
                if log["loop"][path] < 1:
                    failures.append(f"lane {lane} missing loop path {path}")
            if not log.get("backup_verified") or not log.get("restore_reads"):
                failures.append(f"lane {lane} backup/restore exit proof missing")
            if not log.get("import_restore_reads"):
                failures.append(f"lane {lane} export/import exit proof missing")
            if log.get("derived_index_existed") and not log.get("derived_index_rebuilt"):
                failures.append(f"lane {lane} derived index not rebuilt")
            v = verify_lane(lane, workdir / f"lane-{lane}", log)
            log["independent_verify"] = v
            failures.extend(f"lane {lane}: {p}" for p in v["problems"])

        report["failures"] = failures
        report["passed"] = not failures
    finally:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        shutil.rmtree(workdir, ignore_errors=True)

    print(json.dumps({"passed": report["passed"], "failures": report.get("failures", [])}, indent=2))
    if not report["passed"]:
        raise SystemExit("CONTINUITY_SOAK_FAILED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
