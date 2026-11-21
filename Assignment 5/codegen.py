"""Register/address descriptors and a small costed target-code generator."""
class Generator:
    def __init__(self, k=2, strategy="next_use"):
        self.k=k; self.strategy=strategy
        self.regs=[None]*k; self.RDesc=[set() for _ in range(k)]
        self.ADesc={}; self.code=[]; self.loads=0; self.stores=0; self.spills=0
        self.used=set()
    def _where(self, value):
        for r, names in enumerate(self.RDesc):
            if value in names: return r
        return None
    def _load(self, value, avoid=None):
        r=self._where(value)
        if r is not None: return r
        choices=[i for i in range(self.k) if i != avoid]
        free=next((i for i in choices if not self.RDesc[i]), None)
        if free is None:
            if self.strategy=="first": free=choices[0]
            else:
                # Conservative heuristic: evict a register with the fewest aliases.
                free=max(choices, key=lambda x: len(self.RDesc[x]))
            for old in list(self.RDesc[free]):
                if self.ADesc.get(old)=={"mem"} or self.ADesc.get(old)=={free}:
                    self.code.append(f"ST {old}, R{free}"); self.stores+=1
                    self.spills+=1
                    self.ADesc[old]={"mem"}
                self.ADesc.setdefault(old,set()).discard(free)
            self.RDesc[free].clear()
        self.code.append(f"LD R{free}, {value}"); self.loads+=1
        self.RDesc[free].add(value); self.ADesc.setdefault(value,set()).add(free)
        self.used.add(free)
        return free
    def generate(self, instructions):
        for ins in instructions:
            if len(ins)>=4:
                dst, op, a, b = ins
                ra=self._load(a)
                rb=self._load(b, avoid=ra)
                self.code.append(f"{op.upper()} R{ra}, R{rb}")
                self.RDesc[ra].discard(a); self.RDesc[ra].discard(dst)
                self.RDesc[ra].add(dst)
                self.ADesc[dst]={ra}
                if a in self.ADesc: self.ADesc[a].discard(ra)
            else:
                dst, a = ins
                r=self._load(a)
                self.RDesc[r].discard(a); self.RDesc[r].add(dst)
                self.ADesc[dst]={r}
        # Only final values need be committed; demo assumes last destination live.
        if instructions:
            dst=instructions[-1][0]
            r=self._where(dst)
            if r is not None:
                self.code.append(f"ST {dst}, R{r}"); self.stores+=1
        return self.code
    @property
    def cost(self):
        # Cost = 1 + number of memory operands; register operands cost zero.
        return sum(1 + sum(1 for x in line.split(",")[1:] if not x.strip().startswith("R"))
                   for line in self.code)
