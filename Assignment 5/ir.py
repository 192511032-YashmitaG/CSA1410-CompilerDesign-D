"""Three-address IR, basic-block partitioning, CFG and next-use analysis."""
from dataclasses import dataclass, field

@dataclass
class Instr:
    op: str
    dst: str = ""
    a: str = ""
    b: str = ""
    target: int | None = None
    def uses(self):
        if self.op == "if": return [self.a, self.b]
        if self.op == "bin": return [self.a, self.b]
        if self.op == "copy": return [self.a]
        return []
    def defs(self):
        return [self.dst] if self.op in ("bin", "copy") else []

def leaders(code):
    result = {0} if code else set()
    for i, ins in enumerate(code):
        if ins.op in ("goto", "if") and ins.target is not None:
            result.add(ins.target)
            if i + 1 < len(code): result.add(i + 1)
    return sorted(result)

def partition(code):
    ls = leaders(code)
    blocks = []
    for n, start in enumerate(ls):
        end = ls[n+1] if n+1 < len(ls) else len(code)
        if start < end: blocks.append(list(range(start, end)))
    return blocks

def flow_graph(code):
    blocks = partition(code)
    owner = {idx: bi for bi, block in enumerate(blocks) for idx in block}
    succ = {i: [] for i in range(len(blocks))}
    pred = {i: [] for i in range(len(blocks))}
    for bi, block in enumerate(blocks):
        last_i, last = block[-1], code[block[-1]]
        edges = []
        if last.op == "goto":
            edges.append(owner[last.target])
        elif last.op == "if":
            edges.append(owner[last.target])
            if bi + 1 < len(blocks): edges.append(bi + 1)
        elif bi + 1 < len(blocks):
            edges.append(bi + 1)
        succ[bi] = list(dict.fromkeys(edges))
        for nxt in succ[bi]: pred[nxt].append(bi)
    return blocks, succ, pred

def next_use(block, code, live_out=None):
    """Return per-instruction maps. Default: only explicitly live-out names are live."""
    live = set(live_out or ())
    nu = {v: None for v in live}
    result = {}
    for idx in reversed(block):
        ins = code[idx]
        result[idx] = {v: (v in live, nu.get(v)) for v in set(ins.uses()+ins.defs())}
        for d in ins.defs():
            live.discard(d); nu.pop(d, None)
        for u in ins.uses():
            live.add(u); nu[u] = idx
    return result

def sample_loop():
    # A compact CFG equivalent to the assignment's positive-array-sum loop.
    return [
        Instr("copy","s","0"), Instr("copy","i","0"),
        Instr("if",a="i",b="n",target=7), Instr("bin","t1","i","4"),
        Instr("bin","t2","s","t1"), Instr("bin","s","s","t2"),
        Instr("bin","i","i","1"), Instr("goto",target=2),
        Instr("bin","avg","s","n")
    ]
