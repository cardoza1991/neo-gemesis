from __future__ import annotations
import argparse, sys, time
from .sim import Sim

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="neo-genesis")
    p.add_argument("--ticks", type=int, default=2000)
    p.add_argument("--width", type=int, default=48)
    p.add_argument("--height", type=int, default=28)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--seeds", type=int, default=8)
    p.add_argument("--watch", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--delay", type=float, default=0.03)
    args = p.parse_args(argv)
    sim = Sim(width=args.width, height=args.height, seed=args.seed, seeds=args.seeds)
    if args.watch:
        try:
            for _ in range(args.ticks):
                sim.step()
                sys.stdout.write("\033[2J\033[H" + sim.render() + "\n")
                sys.stdout.flush()
                if sim.census().population == 0:
                    break
                time.sleep(args.delay)
        except KeyboardInterrupt:
            pass
    else:
        last = sim.run(args.ticks)
        print(sim.dumps() if args.json else sim.render())
        print(f"done tick={last.tick} pop={last.population} genomes={last.unique_genomes} seed_free={last.seed_free}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
