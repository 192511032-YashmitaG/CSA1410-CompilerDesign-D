"""Small optimisation helpers with explicit safety constraints."""
def constant_fold(op, a, b):
    if not isinstance(a,(int,float)) or not isinstance(b,(int,float)): return None
    if op=="add": return a+b
    if op=="sub": return a-b
    if op=="mul": return a*b
    if op=="div" and b!=0: return a/b
    return None

def dead_assignments(instructions, live_out):
    live=set(live_out); kept=[]
    for ins in reversed(instructions):
        dst=ins[0]
        uses=set(ins[2:]) if len(ins)>2 else {ins[1]}
        if dst in live or ins[1] in ("store","call"):
            kept.append(ins); live.discard(dst); live.update(uses)
    return list(reversed(kept))
