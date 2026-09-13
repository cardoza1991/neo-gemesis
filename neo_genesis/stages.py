"""Stages are earned from physics, not painted on."""
from .isa import Op
STAGE_ORDER = ["Fresh", "In-Training", "Rookie", "Champion", "Ultimate"]

def cluster_sizes(world, organisms):
    seen, sizes = set(), {}
    for oid in organisms:
        if oid in seen:
            continue
        stack, group = [oid], []
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in organisms:
                continue
            seen.add(cur)
            group.append(cur)
            o = organisms[cur]
            for h in range(4):
                nx, ny = world.ahead(o.x, o.y, h)
                nid = world.occupant(nx, ny)
                if nid is not None and nid not in seen:
                    stack.append(nid)
        n = len(group)
        for gid in group:
            sizes[gid] = n
            organisms[gid].cluster = n
    return sizes

def classify(org):
    ops = set(org.genome)
    novel = bool(ops & {Op.EDIT, Op.CONJUGATE, Op.ADHERE, Op.SHARE})
    if org.cluster >= 8 and len(ops) >= 6 and org.adhered:
        return "Ultimate"
    if org.cluster >= 4 and (org.adhered or Op.ADHERE in ops or Op.SHARE in ops):
        return "Champion"
    if novel and (org.divisions > 0 or org.parent is not None) and len(ops) >= 4:
        return "Rookie"
    if org.divisions > 0 or org.parent is not None:
        return "In-Training"
    return "Fresh"

def assign_stages(world, organisms):
    cluster_sizes(world, organisms)
    counts = {s: 0 for s in STAGE_ORDER}
    for org in organisms.values():
        org.stage = classify(org)
        counts[org.stage] = counts.get(org.stage, 0) + 1
    return counts
