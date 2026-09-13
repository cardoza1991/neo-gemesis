# neo-genesis

Repo name is `neo-gemesis` (typo). The project name is **neo-genesis**.

Digital bacteria in a bounded world. Digimon is the ceiling. Prokaryotes are the floor.

**Live dish:** https://cardoza1991.github.io/neo-genesis/

Not `cardoza1991/new_genesis` (GRC swarm). That is a different project.

No language model in the loop. After inoculation the dish runs without a prompt.

## Observed

- Seed-free persistence (ancestors die, population remains).
- Seed 10 in the public dish: t=2598, pop=157, genomes=84, cluster=7, stage=Champion.

## Run

```bash
python3 -m neo_genesis --ticks 1500 --seed 7 --json
python3 -m unittest neo_genesis.test_sim -v
```

Rename the repo in Settings → General → Repository name to `neo-genesis` when you want the URL to match.
