"""Digital bacterium: genome + VM + metabolic budget."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .isa import ADHERE_COST, CONJUGATE_COST, DIVIDE_COST, DIVIDE_RESERVE, EDIT_COST, EAT_RATE, MAX_GENOME, MIN_GENOME, Op, SHARE_AMOUNT, STEP_COST
from .world import World

ANCESTOR = [Op.SENSE, Op.EAT, Op.MOVE, Op.EAT, Op.DIVIDE, Op.TURN_R, Op.EAT, Op.MOVE]

def genome_key(genome):
    return "".join(format(op, "x") for op in genome)

@dataclass
class Organism:
    oid: int
    x: int
    y: int
    heading: int
    energy: float
    genome: list
    parent: Optional[int] = None
    born: int = 0
    ip: int = 0
    sensed: float = 0.0
    divisions: int = 0
    steps: int = 0
    dead: bool = False
    lineage: int = 0
    edits: int = 0
    transfers: int = 0
    adhered: bool = False
    shares: int = 0
    cluster: int = 1
    stage: str = "Fresh"

    def key(self):
        return genome_key(self.genome)

    def execute(self, world, rng, others=None):
        if self.dead:
            return None
        self.energy -= STEP_COST
        self.steps += 1
        if self.energy <= 0:
            self.dead = True
            return None
        op = self.genome[self.ip % len(self.genome)]
        self.ip = (self.ip + 1) % len(self.genome)
        child = None
        if op == Op.TURN_L:
            self.heading = (self.heading - 1) % 4
        elif op == Op.TURN_R:
            self.heading = (self.heading + 1) % 4
        elif op == Op.MOVE:
            if not (self.adhered and rng.random() < 0.7):
                nx, ny = world.ahead(self.x, self.y, self.heading)
                if world.move(self.oid, self.x, self.y, nx, ny):
                    self.x, self.y = nx, ny
                    self.adhered = False
        elif op == Op.SENSE:
            best = world.field_at(self.x, self.y)
            best_h = self.heading
            for h in range(4):
                ax, ay = world.ahead(self.x, self.y, h)
                val = world.field_at(ax, ay)
                if world.vacant(ax, ay) and val > best:
                    best, best_h = val, h
            self.heading = best_h
        elif op == Op.EAT:
            self.energy += world.pull_energy(self.x, self.y, EAT_RATE)
        elif op == Op.DIVIDE:
            child = self.try_divide(world, rng)
        elif op == Op.EDIT:
            self.self_edit(rng)
        elif op == Op.CONJUGATE:
            self.conjugate(world, rng, others)
        elif op == Op.ADHERE:
            self.try_adhere(world, others)
        elif op == Op.SHARE:
            self.share(world, others)
        if self.energy <= 0:
            self.dead = True
            return None
        return child

    def try_divide(self, world, rng):
        if self.energy < DIVIDE_COST + DIVIDE_RESERVE:
            return None
        nx, ny = world.ahead(self.x, self.y, self.heading)
        if not world.vacant(nx, ny):
            found = False
            for h in range(4):
                tx, ty = world.ahead(self.x, self.y, h)
                if world.vacant(tx, ty):
                    nx, ny, found = tx, ty, True
                    break
            if not found:
                return None
        self.energy -= DIVIDE_COST
        given = self.energy * 0.45
        self.energy -= given
        self.divisions += 1
        return Organism(oid=-1, x=nx, y=ny, heading=self.heading, energy=given, genome=mutate(self.genome, rng, rate=stress_rate(self.energy)), parent=self.oid, lineage=self.lineage)

    def self_edit(self, rng):
        if self.energy < EDIT_COST + 1:
            return
        self.energy -= EDIT_COST
        i = rng.randrange(len(self.genome))
        self.genome[i] = needed_op(self.energy, self.sensed, rng)
        self.edits += 1

    def conjugate(self, world, rng, others):
        if not others or self.energy < CONJUGATE_COST + 1:
            return
        nx, ny = world.ahead(self.x, self.y, self.heading)
        oid = world.occupant(nx, ny)
        if oid is None or oid not in others:
            return
        self.energy -= CONJUGATE_COST
        donor = others[oid]
        self.genome[rng.randrange(len(self.genome))] = donor.genome[rng.randrange(len(donor.genome))]
        self.transfers += 1

    def try_adhere(self, world, others):
        self.energy -= ADHERE_COST
        for h in range(4):
            nx, ny = world.ahead(self.x, self.y, h)
            oid = world.occupant(nx, ny)
            if oid is not None:
                self.adhered = True
                if others and oid in others:
                    others[oid].adhered = True
                return

    def share(self, world, others):
        if not others or self.energy < SHARE_AMOUNT + 2:
            return
        nx, ny = world.ahead(self.x, self.y, self.heading)
        oid = world.occupant(nx, ny)
        if oid is None or oid not in others:
            return
        gift = min(SHARE_AMOUNT, self.energy - 1)
        self.energy -= gift
        others[oid].energy += gift
        self.shares += 1
        self.adhered = True

def stress_rate(energy):
    return 0.03 + 0.14 * max(0.0, 1.0 - energy / 36.0)

def needed_op(energy, sensed, rng):
    if energy < 12:
        return rng.choice([Op.EAT, Op.EAT, Op.SENSE, Op.MOVE, Op.EDIT])
    if energy > 28:
        return rng.choice([Op.DIVIDE, Op.EAT, Op.MOVE, Op.CONJUGATE, Op.SHARE])
    return rng.randrange(len(Op))

def mutate(genome, rng, rate=0.04):
    out = list(genome)
    i = 0
    while i < len(out):
        if rng.random() >= rate:
            i += 1
            continue
        kind = rng.random()
        if kind < 0.45:
            out[i] = rng.randrange(len(Op))
        elif kind < 0.7 and len(out) < MAX_GENOME:
            out.insert(i, rng.randrange(len(Op)))
            i += 1
        elif kind < 0.9 and len(out) > MIN_GENOME:
            del out[i]
            continue
        else:
            j = rng.randrange(len(out))
            out[i], out[j] = out[j], out[i]
        i += 1
    return out
