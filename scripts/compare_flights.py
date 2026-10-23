"""Compare Gazebo experiment runs (start_experiment.sh), grouped by algorithm and, for rl, by policy
checkpoint: completion, mission time, distance flown, minimum drone separation (the run summaries) and
minimum obstacle clearance: drone centre to the real obstacle boxes and walls of the factory world in 3-D
(rl-nmopso-factory-patrol/scripts/flight_check.py: above a box top the vertical gap counts), over the
airborne samples (height > 0.3 m) of drone_states.csv. Collision: < 0.3 m; near miss: < 0.6 m.
drone_states.csv is sampled at about 1 Hz, so the true closest approaches can be somewhat smaller.
  python3 scripts/compare_flights.py run_20261022_232247 run_20261022_232438 ... [--out experiment_results/x.json]"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "rl-nmopso-factory-patrol" / "scripts"))
from flight_check import box_clearance, obstacle_boxes  # noqa: E402


def run_stats(rid, boxes):
    d = ROOT / "experiment_results" / rid
    s = next(csv.DictReader(open(next((ROOT / "experiment_results" / "summaries").glob(f"{rid}_*.csv")))))
    ev = [json.loads(line) for line in open(d / "experiment_events.jsonl")]
    group = next((Path(e["path"]).stem for e in ev if e["event_type"] == "rl_policy_loaded"), s["algorithm"])
    X = np.array([[float(r["x"]), float(r["y"]), float(r["z"])] for r in csv.DictReader(open(d / "drone_states.csv"))])
    P = np.c_[X[:, :2], -X[:, 2]]                                       # height = -z (NED down)
    air = P[P[:, 2] > 0.3]
    return group, {"run": rid, "status": s["status"], "completed_tasks": int(s["completed_tasks"]),
                   "total_tasks": int(s["total_tasks"]),
                   "mission_time_s": float(s["mission_completion_time_s"] or "nan"),
                   "distance_m": float(s["total_flight_distance_m"]),
                   "min_separation_m": float(s["minimum_inter_drone_distance_m"]),
                   "min_obstacle_clearance_m": float(box_clearance(air, boxes).min()) if len(air) else None,
                   "rl_plans": sum(e["event_type"] == "rl_plan" for e in ev),
                   "rl_stalls": sum(e["event_type"] == "rl_stall" for e in ev)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", default=None, help="JSON output (default: print only)")
    a = ap.parse_args()
    boxes = obstacle_boxes()
    groups = defaultdict(list)
    for rid in a.runs:
        g, r = run_stats(rid, boxes)
        groups[g].append(r)
    print(f"{'group':10} {'runs':>4} {'completed':>9} {'time s':>13} {'distance m':>14} {'min sep m':>10} {'min clearance m':>15}")
    for g, rs in groups.items():
        f = lambda k: f"{np.mean([r[k] for r in rs]):.1f} ± {np.std([r[k] for r in rs]):.1f}"
        print(f"{g:10} {len(rs):4} {sum(r['status'] == 'completed' for r in rs):5}/{len(rs)} {f('mission_time_s'):>13}"
              f" {f('distance_m'):>14} {min(r['min_separation_m'] for r in rs):10.2f}"
              f" {min(r['min_obstacle_clearance_m'] for r in rs):15.2f}")
    if a.out:
        Path(a.out).write_text(json.dumps(groups, indent=1))
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
