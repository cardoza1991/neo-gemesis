"""World clock, inoculation, census."""
from __future__ import annotations
import json, random
from collections import Counter
from dataclasses import dataclass, field
from .organism import ANCESTOR, Organism
from .stages import assign_stages
from .world import World

@dataclass
class Census:
    tick: int
    population: int
    unique_genomes: int
    total_organism_energy: float
    field_energy: float
    births: int
    deaths: int
    ancestor_alive: bool
    seed_free: bool
    dominant: str
    dominant_count: int
    stages: dict = None
    max_cluster: int = 1

@dataclass
class Sim:
    width: int = 48
    height: int = 28
    seed: int = 1
    seeds: int = 8
    steps_per_tick: int = 3
    max_pop: int = 400
    world: World = field(init=False)
    rng: random.Random = field(init=False)
    organisms: dict = field(default_factory=dict)
    next_id: int = 1
    tick: int = 0
    births: int = 0
    deaths: int = 0
    seed_ids: set = field(default_factory=set)
    history: list = field(default_factory=list)

    def __post_init__(self):
        self.world = World(self.width, self.height)
        self.rng = random.Random(self.seed)
        self.inoculate()

    def inoculate(self):
        placed = attempts = 0
        while placed < self.seeds and attempts < self.seeds * 40:
            attempts += 1
            x, y = self.rng.randrange(self.width), self.rng.randrange(self.height)
            if not self.world.vacant(x, y):
                continue
            org = Organism(oid=self.next_id, x=x, y=y, heading=self.rng.randrange(4), energy=40.0, genome=list(ANCESTOR), lineage=self.next_id)
            self.world.place(org.oid, x, y)
            self.organisms[org.oid] = org
            self.seed_ids.add(org.oid)
            self.next_id += 1
            placed += 1

    def step(self):
        self.tick += 1
        order = list(self.organisms)
        self.rng.shuffle(order)
        newborns = []
        for _ in range(self.steps_per_tick):
            for oid in order:
                org = self.organisms.get(oid)
                if org is None or org.dead:
                    continue
                child = org.execute(self.world, self.rng, self.organisms)
                if child is not None and len(self.organisms) + len(newborns) < self.max_pop:
                    child.oid = self.next_id
                    child.born = self.tick
                    self.next_id += 1
                    if self.world.vacant(child.x, child.y):
                        self.world.place(child.oid, child.x, child.y)
                        newborns.append(child)
                        self.births += 1
        for child in newborns:
            self.organisms[child.oid] = child
        for oid in [i for i, o in self.organisms.items() if o.dead or o.energy <= 0]:
            org = self.organisms.pop(oid)
            self.world.clear(org.x, org.y)
            self.deaths += 1
        self.world.tick_field()
        stages = assign_stages(self.world, self.organisms)
        census = self.census()
        census.stages = stages
        census.max_cluster = max((o.cluster for o in self.organisms.values()), default=0)
        return census

    def run(self, ticks):
        last = self.census()
        for _ in range(ticks):
            last = self.step()
            if last.population == 0:
                break
        return last

    def census(self):
        keys = [o.key() for o in self.organisms.values()]
        counts = Counter(keys)
        dominant, n = counts.most_common(1)[0] if counts else ("", 0)
        ancestor_alive = any(i in self.organisms for i in self.seed_ids)
        return Census(tick=self.tick, population=len(self.organisms), unique_genomes=len(counts), total_organism_energy=sum(o.energy for o in self.organisms.values()), field_energy=self.world.total_field(), births=self.births, deaths=self.deaths, ancestor_alive=ancestor_alive, seed_free=(not ancestor_alive and len(self.organisms) > 0), dominant=dominant, dominant_count=n)

    def render(self):
        assign_stages(self.world, self.organisms)
        mx = max((o.cluster for o in self.organisms.values()), default=0)
        rows = [f"t={self.tick} pop={len(self.organisms)} seed_free={self.census().seed_free} cluster_max={mx}"]
        occ = {(o.x, o.y): o for o in self.organisms.values()}
        for y in range(self.height):
            line = []
            for x in range(self.width):
                o = occ.get((x, y))
                if o:
                    line.append("#" if o.cluster >= 8 else "O" if o.cluster >= 4 else "o")
                else:
                    e = self.world.energy[y][x]
                    line.append(" " if e < 1 else "." if e < 5 else ":")
            rows.append("".join(line))
        return "\n".join(rows)

    def snapshot(self):
        c = self.census()
        return {"tick": c.tick, "population": c.population, "unique_genomes": c.unique_genomes, "births": c.births, "deaths": c.deaths, "seed_free": c.seed_free, "max_cluster": max((o.cluster for o in self.organisms.values()), default=0), "stages": assign_stages(self.world, self.organisms)}

    def dumps(self):
        return json.dumps(self.snapshot(), indent=2)
