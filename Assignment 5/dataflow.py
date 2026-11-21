"""Bit-set data-flow analyses: reaching definitions, liveness and available expressions."""
def reaching_definitions(blocks, gen, kill, order=None):
    n=len(blocks); order=order or list(range(n))
    IN=[set() for _ in range(n)]; OUT=[set(gen[i]) for i in range(n)]
    pred=blocks
    changed=True; visits=0
    while changed:
        changed=False
        for b in order:
            visits+=1
            new_in=set().union(*(OUT[p] for p in pred[b])) if pred[b] else set()
            new_out=set(gen[b]) | (new_in-set(kill[b]))
            if new_in!=IN[b] or new_out!=OUT[b]:
                IN[b],OUT[b]=new_in,new_out; changed=True
    return IN,OUT,visits

def liveness(succ, use, defs, order=None):
    n=len(succ); order=order or list(reversed(range(n)))
    IN=[set() for _ in range(n)]; OUT=[set() for _ in range(n)]
    changed=True; visits=0
    while changed:
        changed=False
        for b in order:
            visits+=1
            out=set().union(*(IN[s] for s in succ[b])) if succ[b] else set()
            inside=set(use[b]) | (out-set(defs[b]))
            if out!=OUT[b] or inside!=IN[b]:
                OUT[b],IN[b]=out,inside; changed=True
    return IN,OUT,visits

def available_expressions(pred, gen, kill, universe, order=None):
    n=len(pred); order=order or list(range(n))
    IN=[set(universe) for _ in range(n)]; OUT=[set(universe) for _ in range(n)]
    if n: IN[0]=set()
    changed=True; visits=0
    while changed:
        changed=False
        for b in order:
            visits+=1
            incoming=(set.intersection(*(OUT[p] for p in pred[b])) if pred[b] else set())
            outgoing=set(gen[b]) | (incoming-set(kill[b]))
            if incoming!=IN[b] or outgoing!=OUT[b]:
                IN[b],OUT[b]=incoming,outgoing; changed=True
    return IN,OUT,visits
