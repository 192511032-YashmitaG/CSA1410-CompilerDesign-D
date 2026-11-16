# sdt.py - Assignment 3 (CO3): Syntax-Directed Translation, all experiments
import re, time, sys, tracemalloc
from collections import deque

class SyntaxErr(Exception): pass
def fmt(v):
    return str(int(v)) if float(v) == int(v) else str(round(v, 4))

# ------------------------------------------------------------------ Q1
class Node:
    __slots__ = ('sym', 'kids', 'lex', 'val', 'h', 'id')
    def __init__(s, sym, kids=None, lex=None):
        s.sym = sym; s.kids = kids or []; s.lex = lex; s.val = None; s.h = None; s.id = None

def tokenize(s, single=True):
    if single:
        out = []
        for ch in s:
            if ch.isspace(): continue
            if ch in '+-*/()=' or ch.isdigit() or ch.isalpha(): out.append(ch)
            else: raise SyntaxErr("illegal character '%s'" % ch)
        return out
    return re.findall(r'[A-Za-z_]\w*|\d+|[-+*/()=]', s)

class LParser:
    """Left-recursive grammar (E->E+T|E-T|T ...) realised with loops; builds parse tree."""
    def __init__(s, toks): s.t = toks + ['$']; s.i = 0
    def peek(s): return s.t[s.i]
    def nxt(s): c = s.t[s.i]; s.i += 1; return c
    def parse(s):
        n = s.E()
        if s.peek() != '$': raise SyntaxErr("unexpected '%s' at token %d" % (s.peek(), s.i + 1))
        return n
    def E(s):
        n = Node('E', [s.T()])
        while s.peek() in ('+', '-'):
            op = s.nxt(); n = Node('E', [n, Node(op, lex=op), s.T()])
        return n
    def T(s):
        n = Node('T', [s.F()])
        while s.peek() in ('*', '/'):
            op = s.nxt(); n = Node('T', [n, Node(op, lex=op), s.F()])
        return n
    def F(s):
        c = s.peek()
        if c == '(':
            s.nxt(); e = s.E()
            if s.peek() != ')': raise SyntaxErr("missing ')' at token %d" % (s.i + 1))
            s.nxt(); return Node('F', [Node('(', lex='('), e, Node(')', lex=')')])
        if c.isdigit():
            s.nxt(); return Node('F', [Node('digit', lex=c)])
        if c[0].isalpha() or c[0] == '_':
            s.nxt(); return Node('F', [Node('id', lex=c)])
        raise SyntaxErr("unexpected '%s' at token %d" % (c, s.i + 1))

class RParser(LParser):
    """Right-recursive version: E->T+E|T-E|T ; T->F*T|F/T|F"""
    def E(s):
        t = s.T()
        if s.peek() in ('+', '-'):
            op = s.nxt(); return Node('E', [t, Node(op, lex=op), s.E()])
        return Node('E', [t])
    def T(s):
        f = s.F()
        if s.peek() in ('*', '/'):
            op = s.nxt(); return Node('T', [f, Node(op, lex=op), s.T()])
        return Node('T', [f])

OPS = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b,
       '/': lambda a, b: a / b}

def evaluate(n):
    """post-order evaluation of the synthesized attribute val; returns #rules fired"""
    cnt = 0
    for k in n.kids: cnt += evaluate(k)
    if n.sym == 'digit': n.val = int(n.lex); return cnt
    if n.sym in ('id', '+', '-', '*', '/', '(', ')'): return cnt
    if n.sym == 'F':
        n.val = n.kids[0].val if n.kids[0].sym == 'digit' else n.kids[1].val
    elif len(n.kids) == 1: n.val = n.kids[0].val
    else:
        op = n.kids[1].sym
        if op == '/' and n.kids[2].val == 0: raise ZeroDivisionError("division by zero")
        n.val = OPS[op](n.kids[0].val, n.kids[2].val)
    return cnt + 1

def height(n):
    n.h = 0 if not n.kids else 1 + max(height(k) for k in n.kids)
    return n.h

def count(n): return 1 + sum(count(k) for k in n.kids)
def count_nt(n): return (1 if n.kids else 0) + sum(count_nt(k) for k in n.kids)

def tree_lines(n, d=0, show_h=False):
    if n.sym == 'digit': txt = "digit(%s)  lexval=%s" % (n.lex, n.lex)
    elif n.sym == 'id': txt = "id(%s)" % n.lex
    elif not n.kids: txt = "'%s'" % n.sym
    else:
        txt = "%s  val=%s" % (n.sym, fmt(n.val)) if n.val is not None else n.sym
        if show_h: txt += "  height=%d" % n.h
    out = [(d, txt)]
    for k in n.kids: out += tree_lines(k, d + 1, show_h)
    return out

def q1_tests():
    tests = [("7", 7), ("(((7)))", 7), ("8-3-2", 3), ("2*3+4*5", 26), ("3*(4+5)-6/2", 24),
             ("9/3/3", 1), ("((1+2)*(3+4))-5", 16), ("7/2", 3.5), ("3+*4", None), ("(2+3", None)]
    res = []
    for e, hand in tests:
        try:
            root = LParser(tokenize(e)).parse(); ev = evaluate(root); height(root)
            res.append(dict(e=e, hand=hand, prog=root.val, ok=(hand == root.val), nodes=count(root),
                            nt=count_nt(root), ev=ev, h=root.h, toks=len(e)))
        except SyntaxErr as x:
            res.append(dict(e=e, hand=hand, err=str(x)))
    return res

def chain(n, op='+'): return op.join(['1'] * n)
def height_experiment(ns=(1, 2, 4, 8, 16, 32, 64, 128)):
    rows = []
    for n in ns:
        e = chain(n); tl = len(e)
        L = LParser(tokenize(e)).parse(); evaluate(L); height(L)
        R = RParser(tokenize(e)).parse(); evaluate(R); height(R)
        rows.append((n, tl, count(L), L.h, R.h))
    nest = []
    for k in (1, 2, 4, 8, 16):
        e = '(' * k + '1' + ')' * k
        L = LParser(tokenize(e)).parse(); evaluate(L); height(L)
        nest.append((k, len(e), count(L), L.h))
    return rows, nest

def assoc_demo():
    out = []
    for e in ("8-3-2", "9/3/3"):
        L = LParser(tokenize(e)).parse(); evaluate(L)
        R = RParser(tokenize(e)).parse(); evaluate(R)
        out.append((e, L.val, R.val))
    return out

# ------------------------------------------------------------------ Q2
class DeclError(Exception): pass

def parse_decl(src):
    """D -> T L ; L -> L , id | id  (left recursive, built with a loop)"""
    t = re.findall(r'[A-Za-z_]\w*|,', src)
    if not t or t[0] not in ('int', 'float'): raise SyntaxErr("declaration must start with int/float")
    T = Node('T', [Node(t[0], lex=t[0])]); i = 1
    if i >= len(t) or t[i] in (',', 'int', 'float'): raise SyntaxErr("identifier expected after type")
    L = Node('L', [Node('id', lex=t[i])]); i += 1
    while i < len(t):
        if t[i] != ',': raise SyntaxErr("',' expected, found '%s'" % t[i])
        i += 1
        if i >= len(t) or t[i] in (',', 'int', 'float'): raise SyntaxErr("identifier expected after ','")
        L = Node('L', [L, Node(',', lex=','), Node('id', lex=t[i])]); i += 1
    return Node('D', [T, L])

def decl_semantics(D, table, log):
    """T.type synthesized, L.in inherited, addType through the actions"""
    T, L = D.kids
    T.val = T.kids[0].sym; log.append("T.type = %s   (synthesized from child '%s')" % (T.val, T.val))
    def visit(l, inh):
        l.h = inh                      # store L.in in slot h
        log.append("L.in  = %s   (inherited)" % inh)
        if len(l.kids) == 1: act(l.kids[0], inh)
        else:
            visit(l.kids[0], inh)       # L1.in = L.in
            act(l.kids[2], inh)
    def act(idn, ty):
        name = idn.lex
        if name in table: raise DeclError("'%s' is already declared as %s" % (name, table[name]))
        table[name] = ty; idn.val = ty
        log.append("addType(%s, %s)" % (name, ty))
    visit(L, T.val)

def decl_tree_lines(n, d=0, parent_note=''):
    if n.sym == 'id': txt = "id(%s)  type=%s" % (n.lex, n.val)
    elif n.sym in ('int', 'float'): txt = "'%s'" % n.sym
    elif n.sym == ',': txt = "','"
    elif n.sym == 'T': txt = "T  type=%s   (synthesized)" % n.val
    elif n.sym == 'L': txt = "L  in=%s   (inherited)" % n.h
    else: txt = n.sym
    out = [(d, txt)]
    for k in n.kids: out += decl_tree_lines(k, d + 1)
    return out

def q2_tests():
    cases = ["float a, b, c", "int x", "int a, b, a", "float p, , q", "int i, j, k, n"]
    res = []
    for c in cases:
        table = {}; log = []
        try:
            D = parse_decl(c); decl_semantics(D, table, log)
            res.append(dict(src=c, ok=True, table=dict(table), log=log, tree=D))
        except (SyntaxErr, DeclError) as x:
            res.append(dict(src=c, ok=False, err=("%s: %s" % ("syntax error" if isinstance(x, SyntaxErr) else "semantic error", x)),
                            table=dict(table), log=log))
    return res

def use_check(table, names):
    return [(n, table.get(n, None)) for n in names]

# ------------------------------------------------------------------ Q3 generic evaluator
class AttrGraph:
    def __init__(s): s.deps = {}; s.fn = {}; s.val = {}
    def add(s, name, deps, fn): s.deps[name] = list(deps); s.fn[name] = fn
    def edges(s): return [(d, n) for n in s.deps for d in s.deps[n]]
    def kahn(s):
        indeg = {n: len(s.deps[n]) for n in s.deps}
        users = {n: [] for n in s.deps}
        for n in s.deps:
            for d in s.deps[n]: users[d].append(n)
        q = deque(n for n in s.deps if indeg[n] == 0); order = []
        while q:
            u = q.popleft(); order.append(u)
            for v in users[u]:
                indeg[v] -= 1
                if indeg[v] == 0: q.append(v)
        return order, [n for n in s.deps if indeg[n] > 0]
    def dfs_order(s):
        seen = set(); out = []
        def go(n):
            if n in seen: return
            seen.add(n)
            for d in reversed(s.deps[n]): go(d)
            out.append(n)
        for n in reversed(list(s.deps)): go(n)
        return out
    def run(s, order):
        s.val = {}
        for n in order: s.val[n] = s.fn[n](*[s.val[d] for d in s.deps[n]])
        return s.val
    def find_cycle(s, leftover):
        start = leftover[0]; path = [start]; cur = start
        while True:
            nxt = next(d for d in s.deps[cur] if d in leftover)
            if nxt in path: return path[path.index(nxt):] + [nxt]
            path.append(nxt); cur = nxt

def number_nodes(n, c=None):
    c = c if c is not None else [0]
    n.id = c[0]; c[0] += 1
    for k in n.kids: number_nodes(k, c)

def nm(n): return "%s%d" % (n.sym if n.sym not in '+-*/()' else {'+': 'plus', '-': 'minus', '*': 'times', '/': 'div', '(': 'lp', ')': 'rp'}[n.sym], n.id)

def expr_graph(src):
    root = LParser(tokenize(src)).parse(); number_nodes(root)
    g = AttrGraph(); info = []
    def go(n):
        if n.sym == 'digit':
            g.add(nm(n) + ".lexval", [], lambda v=int(n.lex): v); return nm(n) + ".lexval"
        if not n.kids: return None
        ks = [go(k) for k in n.kids]
        me = nm(n) + ".val"
        if n.sym == 'F':
            src_ = ks[0] if n.kids[0].sym == 'digit' else ks[1]
            g.add(me, [src_], lambda x: x)
        elif len(n.kids) == 1: g.add(me, [ks[0]], lambda x: x)
        else:
            op = n.kids[1].sym
            g.add(me, [ks[0], ks[2]], lambda a, b, op=op: OPS[op](a, b))
        return me
    top = go(root)
    return root, g, top

def decl_graph(src="float a, b"):
    D = parse_decl(src); T, L = D.kids
    ids = []
    def collect(l):
        if len(l.kids) == 1: ids.append(l.kids[0].lex)
        else: collect(l.kids[0]); ids.append(l.kids[2].lex)
    collect(L)
    g = AttrGraph(); g.add("T.type", [], lambda: T.kids[0].sym)
    g.add("L_%s.in" % ids[-1], ["T.type"], lambda x: x)
    prev = "L_%s.in" % ids[-1]
    for k in range(len(ids) - 1, 0, -1):
        cur = "L_%s.in" % ids[k - 1]
        g.add(cur, [prev], lambda x: x)
        g.add("id_%s.type" % ids[k], [prev], lambda x: x)
        prev = cur
    g.add("id_%s.type" % ids[0], [prev], lambda x: x)
    return g

def cyclic_graph():
    g = AttrGraph()
    g.add("A.s", ["B.i"], lambda x: x + 1)
    g.add("B.i", ["A.s"], lambda x: x + 1)
    g.add("C.v", [], lambda: 0)
    return g

# ------------------------------------------------------------------ Q4 postfix SDT
def tok4(s): return re.findall(r'[A-Za-z_]\w*|\d+|[-+*/()]', s)

class PostfixSDT:
    """E->E+T {print +} | E-T {print -} | T ; T->T*F {print *} | T/F {print /} | F ; F->(E) | id {print id}"""
    def __init__(s, toks, mode='end'): s.t = toks + ['$']; s.i = 0; s.out = []; s.act = 0; s.mode = mode
    def peek(s): return s.t[s.i]
    def nxt(s): c = s.t[s.i]; s.i += 1; return c
    def emit(s, x): s.out.append(x); s.act += 1
    def parse(s):
        s.E()
        if s.peek() != '$': raise SyntaxErr("unexpected '%s'" % s.peek())
        return ' '.join(s.out)
    def E(s):
        s.T()
        while s.peek() in '+-' and s.peek() != '$':
            op = s.nxt()
            if s.mode == 'mid': s.emit(op)
            s.T()
            if s.mode == 'end': s.emit(op)
    def T(s):
        s.F()
        while s.peek() in ('*', '/'):
            op = s.nxt()
            if s.mode == 'mid': s.emit(op)
            s.F()
            if s.mode == 'end': s.emit(op)
    def F(s):
        c = s.peek()
        if c == '(':
            s.nxt(); s.E()
            if s.peek() != ')': raise SyntaxErr("missing ')'")
            s.nxt()
        elif c[0].isalnum() or c[0] == '_': s.nxt(); s.emit(c)
        else: raise SyntaxErr("unexpected '%s'" % c)

class PostfixTopDown:
    """left recursion removed: E->T E' ; E'->+ T {print +} E' | - T {print -} E' | eps"""
    def __init__(s, toks): s.t = toks + ['$']; s.i = 0; s.out = []; s.act = 0
    def peek(s): return s.t[s.i]
    def nxt(s): c = s.t[s.i]; s.i += 1; return c
    def emit(s, x): s.out.append(x); s.act += 1
    def parse(s): s.E(); return ' '.join(s.out)
    def E(s): s.T(); s.Ep()
    def Ep(s):
        if s.peek() in ('+', '-'):
            op = s.nxt(); s.T(); s.emit(op); s.Ep()
    def T(s): s.F(); s.Tp()
    def Tp(s):
        if s.peek() in ('*', '/'):
            op = s.nxt(); s.F(); s.emit(op); s.Tp()
    def F(s):
        c = s.peek()
        if c == '(':
            s.nxt(); s.E(); s.nxt()
        else: s.nxt(); s.emit(c)

def shunting(toks):
    prec = {'+': 1, '-': 1, '*': 2, '/': 2}; out = []; st = []
    for t in toks:
        if t == '(': st.append(t)
        elif t == ')':
            while st[-1] != '(': out.append(st.pop())
            st.pop()
        elif t in prec:
            while st and st[-1] in prec and prec[st[-1]] >= prec[t]: out.append(st.pop())
            st.append(t)
        else: out.append(t)
    while st: out.append(st.pop())
    return ' '.join(out)

def postfix_eval(pf, env):
    st = []
    for t in pf.split():
        if t in OPS: b = st.pop(); a = st.pop(); st.append(OPS[t](a, b))
        else: st.append(env[t] if t in env else float(t))
    return st[0]

def q4_tests():
    exprs = ["a+b*(c-d)", "a-b-c", "a*b+c*d", "(a+b)*(c-d)", "a/b/c", "a+b+c*d-e", "((a))", "a-(b-c)"]
    env = {'a': 8, 'b': 4, 'c': 2, 'd': 1, 'e': 3}
    res = []
    for e in exprs:
        toks = tok4(e)
        p = PostfixSDT(toks); pf = p.parse()
        q = PostfixTopDown(toks); pf2 = q.parse()
        m = PostfixSDT(toks, 'mid'); mf = m.parse()
        ref = shunting(toks)
        # evaluate infix with the Q1 parser (letters as ids) through python eval for value check
        val_pf = postfix_eval(pf, env)
        val_inf = eval(e.replace('/', '/'), {}, env)
        res.append(dict(e=e, pf=pf, ref=ref, ok=(pf == ref), td=(pf2 == pf), act=p.act, mid=mf,
                        v1=val_pf, v2=val_inf))
    sizes = []
    for n in (1, 2, 4, 8, 16, 32, 64, 128, 256):
        e = '+'.join(['a*b'] * n) if n > 1 else 'a*b'
        toks = tok4(e); p = PostfixSDT(toks); p.parse()
        root = LParser(tokenize(e.replace('a', '1').replace('b', '2'))).parse(); ev = evaluate(root)
        sizes.append((len(toks), p.act, count(root), ev))
    return res, sizes

# ------------------------------------------------------------------ Q5 AST
class AST:
    __slots__ = ('op', 'l', 'r', 'name')
    def __init__(s, op, l=None, r=None, name=None): s.op = op; s.l = l; s.r = r; s.name = name
def mkNode(op, l, r): return AST(op, l, r)
def mkLeaf(name): return AST('leaf', name=name)
def ast_lines(a, d=0):
    if a.op == 'leaf': return [(d, a.name)]
    return [(d, a.op)] + ast_lines(a.l, d + 1) + ast_lines(a.r, d + 1)
def ast_count(a): return 1 if a.op == 'leaf' else 1 + ast_count(a.l) + ast_count(a.r)
def ast_str(a): return a.name if a.op == 'leaf' else "(%s %s %s)" % (ast_str(a.l), a.op, ast_str(a.r))

def parse_tree_full(src):
    t = tokenize(src, single=False)
    if len(t) >= 2 and t[1] == '=':
        rhs = LParser(t[2:]).parse(); S = Node('S', [Node('id', lex=t[0]), Node('=', lex='='), rhs])
        return S
    return LParser(t).parse()

def ast_bottom_up(toks):
    """E.node via synthesized attribute only: E->E+T {E.node=mkNode('+',E1.node,T.node)}"""
    t = toks + ['$']; i = [0]
    def pk(): return t[i[0]]
    def nx(): c = t[i[0]]; i[0] += 1; return c
    def E():
        n = T()
        while pk() in ('+', '-'): op = nx(); n = mkNode(op, n, T())
        return n
    def T():
        n = F()
        while pk() in ('*', '/'): op = nx(); n = mkNode(op, n, F())
        return n
    def F():
        c = nx()
        if c == '(': e = E(); nx(); return e
        return mkLeaf(c)
    if len(toks) > 1 and toks[1] == '=':
        i[0] = 2; return mkNode('=', mkLeaf(toks[0]), E())
    return E()

def ast_top_down(toks):
    """E->T E' {E'.inh=T.node; E.node=E'.syn}; E'->+T {E1'.inh=mkNode(+,E'.inh,T.node)} E1' {E'.syn=E1'.syn}; E'->eps {E'.syn=E'.inh}"""
    t = toks + ['$']; i = [0]
    def pk(): return t[i[0]]
    def nx(): c = t[i[0]]; i[0] += 1; return c
    def E(): return Ep(T())
    def Ep(inh):
        if pk() in ('+', '-'):
            op = nx(); tn = T(); return Ep(mkNode(op, inh, tn))
        return inh
    def T(): return Tp(F())
    def Tp(inh):
        if pk() in ('*', '/'):
            op = nx(); f = F(); return Tp(mkNode(op, inh, f))
        return inh
    def F():
        c = nx()
        if c == '(': e = E(); nx(); return e
        return mkLeaf(c)
    if len(toks) > 1 and toks[1] == '=':
        i[0] = 2; return mkNode('=', mkLeaf(toks[0]), E())
    return E()

def q5_counts():
    inputs = ["a", "a+b", "a+b*c", "a=b+c*d", "((a))", "a=b+c*d-e/f", "a+b+c+d+e+f+g+h"]
    rows = []
    for e in inputs:
        p = parse_tree_full(e); toks = tokenize(e, single=False)
        a = ast_bottom_up(toks); a2 = ast_top_down(toks)
        rows.append((e, len(toks), count(p), ast_count(a), ast_str(a) == ast_str(a2)))
    gr = []
    for n in (2, 4, 8, 16, 32, 64, 128):
        e = '+'.join(['a'] * n); toks = tokenize(e, single=False)
        gr.append((n, len(toks), count(parse_tree_full(e)), ast_count(ast_bottom_up(toks))))
    nest = []
    for k in (1, 4, 16):
        e = '(' * k + 'a' + ')' * k; toks = tokenize(e, single=False)
        nest.append((k, len(toks), count(parse_tree_full(e)), ast_count(ast_bottom_up(toks))))
    return rows, gr, nest

def q5_memory():
    out = []
    for n in (10, 100, 1000):
        e = '+'.join(['a'] * n); toks = tokenize(e, single=False)
        tracemalloc.start(); p = LParser(toks).parse(); pm = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
        tracemalloc.start(); a = ast_bottom_up(toks); am = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
        out.append((n, pm, am, round(pm / am, 1)))
    return out

# ------------------------------------------------------------------ Q6
def tac_expr(a, gen, wrong=False):
    """E.addr and E.code as synthesized attributes. returns (addr, code list)"""
    if a.op == 'leaf': return a.name, []
    if a.op == '=':
        ad, code = tac_expr(a.r, gen, wrong)
        return a.l.name, code + ["%s = %s" % (a.l.name, ad)]
    a1, c1 = tac_expr(a.l, gen, wrong); a2, c2 = tac_expr(a.r, gen, wrong)
    t = gen.newTemp(); g = "%s = %s %s %s" % (t, a1, a.op, a2)
    return (t, [g] + c1 + c2) if wrong else (t, c1 + c2 + [g])

class TG:
    def __init__(s): s.n = 0
    def newTemp(s): s.n += 1; return "t%d" % s.n

def q6_tac(src, wrong=False):
    a = ast_bottom_up(tokenize(src, single=False)); g = TG()
    ad, code = tac_expr(a, g, wrong); return code

def marker_trace():
    """shift-reduce parse of  int x , y  with D -> T M L ; M -> eps ; L -> L , id | id"""
    stack = []; table = {}; trace = []
    def show(action, note=""):
        trace.append((action, "  ".join(stack), note))
    inp = ['int', 'x', ',', 'y']
    show("start")
    stack.append("int");                                   show("shift int")
    stack[-1] = "T(type=int)";                             show("reduce T -> int", "T.type = int")
    stack.append("M(s=int)");                              show("reduce M -> eps", "M.s = val[top] = int")
    stack.append("x");                                     show("shift id(x)")
    ty = "int"; table['x'] = ty; stack[-1] = "L";          show("reduce L -> id", "addType(x, val[top-1].s) = int")
    stack.append(",");                                     show("shift ','")
    stack.append("y");                                     show("shift id(y)")
    table['y'] = "int"; del stack[-3:]; stack.append("L"); show("reduce L -> L , id", "addType(y, val[top-3].s) = int")
    del stack[:]; stack.append("D");                       show("reduce D -> T M L")
    show("accept", "symbol table: " + ", ".join("%s:%s" % kv for kv in table.items()))
    return trace

# ------------------------------------------------------------------ Q7  MiniLang translator
class CompileError(Exception):
    def __init__(s, line, msg): s.line = line; s.msg = msg; Exception.__init__(s, "line %d: %s" % (line, msg))

TOKRE = re.compile(r'(\d+\.\d+|\d+)|([A-Za-z_]\w*)|(==|!=|<=|>=|[-+*/=<>(){};,])|(\S)')
def lex(src):
    toks = []; line = 1; pos = 0
    for m in TOKRE.finditer(src):
        line += src.count('\n', pos, m.start()); pos = m.start()
        if m.group(1): toks.append(('num', m.group(1), line))
        elif m.group(2): toks.append(('kw' if m.group(2) in ('int', 'float', 'if', 'else', 'while') else 'id', m.group(2), line))
        elif m.group(3): toks.append(('op', m.group(3), line))
        else: toks.append(('bad', m.group(4), line))
    toks.append(('eof', '$', line)); return toks

class A:
    __slots__ = ('k', 'kids', 'v', 'line', 'ty', 'addr')
    def __init__(s, k, kids=(), v=None, line=0): s.k = k; s.kids = list(kids); s.v = v; s.line = line; s.ty = None; s.addr = None

class Lab:
    __slots__ = ('name',)
    def __init__(s): s.name = None

class Gen:
    def __init__(s): s.code = []; s.nt = 0; s.nl = 0
    def temp(s): s.nt += 1; return "t%d" % s.nt
    def label(s): return Lab()
    def emit(s, x): s.code.append("    " + x)
    def jump(s, l):
        if l.name is None: s.nl += 1; l.name = "L%d" % s.nl
        return l.name
    def place(s, l): s.code.append(s.jump(l) + ":")
    def place_if_used(s, l):
        if l.name is not None: s.place(l)
    def coerce(s, a): t = s.temp(); s.emit("%s = (float) %s" % (t, a)); return t
    def binop(s, op, x, y):
        (a, ta), (b, tb) = x, y
        ty = 'float' if 'float' in (ta, tb) else 'int'
        if ty == 'float':
            if ta == 'int': a = s.coerce(a)
            if tb == 'int': b = s.coerce(b)
        t = s.temp(); s.emit("%s = %s %s %s" % (t, a, op, b)); return (t, ty)
    def relop(s, op, x, y, lt, lf):
        (a, ta), (b, tb) = x, y
        if 'float' in (ta, tb):
            if ta == 'int': a = s.coerce(a)
            if tb == 'int': b = s.coerce(b)
        s.emit("if %s %s %s goto %s" % (a, op, b, s.jump(lt))); s.emit("goto %s" % s.jump(lf))
    def assign(s, name, nty, x, line):
        a, ty = x
        if nty == 'int' and ty == 'float': raise CompileError(line, "cannot assign float expression to int variable '%s'" % name)
        if nty == 'float' and ty == 'int': a = s.coerce(a)
        s.emit("%s = %s" % (name, a))

class MiniLang:
    def __init__(s, src, mode):
        s.toks = lex(src); s.i = 0; s.mode = mode; s.sym = {}; s.errors = []; s.g = Gen(); s.ast = []
    def pk(s): return s.toks[s.i]
    def nx(s): t = s.toks[s.i]; s.i += 1; return t
    def is_(s, text): return s.pk()[1] == text and s.pk()[0] in ('op', 'kw')
    def expect(s, text):
        t = s.pk()
        if t[1] != text or t[0] not in ('op', 'kw'): raise CompileError(t[2], "syntax error: expected '%s' but found '%s'" % (text, t[1]))
        s.i += 1
    # ---- declarations: D -> (int|float) L ; ; L.in inherited (parameter), addType via the action
    def decls(s):
        while s.pk()[1] in ('int', 'float') and s.pk()[0] == 'kw':
            ty = s.nx()[1]                         # T.type (synthesized)
            while True:                            # L -> L , id | id   (L.in = ty is passed down)
                t = s.nx()
                try:
                    if t[0] != 'id': raise CompileError(t[2], "syntax error: identifier expected")
                    if t[1] in s.sym: raise CompileError(t[2], "duplicate declaration of '%s'" % t[1])
                    s.sym[t[1]] = ty               # addType(id.entry, L.in)
                except CompileError as e: s.errors.append(str(e))
                if s.is_(','): s.nx(); continue
                break
            try: s.expect(';')
            except CompileError as e: s.errors.append(str(e)); s.sync()
    def sync(s):
        while s.pk()[0] != 'eof' and not (s.is_(';') or s.is_('}')): s.nx()
        if s.is_(';'): s.nx()
    # ---- expressions (E.addr, E.type synthesized)
    def expr(s):
        l = s.term()
        while s.pk()[1] in ('+', '-') and s.pk()[0] == 'op':
            op = s.nx()[1]; r = s.term(); l = s.mkbin(op, l, r)
        return l
    def term(s):
        l = s.factor()
        while s.pk()[1] in ('*', '/') and s.pk()[0] == 'op':
            op = s.nx()[1]; r = s.factor(); l = s.mkbin(op, l, r)
        return l
    def factor(s):
        t = s.pk()
        if t[1] == '(' and t[0] == 'op':
            s.nx(); e = s.expr(); s.expect(')'); return e
        if t[0] == 'num':
            s.nx(); ty = 'float' if '.' in t[1] else 'int'
            return (t[1], ty) if s.mode == 'sdt' else A('num', v=t[1], line=t[2])
        if t[0] == 'id':
            s.nx()
            if s.mode == 'sdt':
                if t[1] not in s.sym: raise CompileError(t[2], "undeclared variable '%s'" % t[1])
                return (t[1], s.sym[t[1]])
            return A('id', v=t[1], line=t[2])
        raise CompileError(t[2], "syntax error: unexpected '%s'" % t[1])
    def mkbin(s, op, l, r): return s.g.binop(op, l, r) if s.mode == 'sdt' else A('bin', [l, r], op)
    # ---- conditions and statements ;  S.next is the inherited attribute (parameter nxt)
    def cond(s, lt, lf):
        l = s.expr(); t = s.pk()
        if t[1] not in ('<', '>', '<=', '>=', '==', '!=') or t[0] != 'op': raise CompileError(t[2], "syntax error: relational operator expected")
        s.nx(); r = s.expr()
        if s.mode == 'sdt': s.g.relop(t[1], l, r, lt, lf); return None
        return A('rel', [l, r], t[1])
    def stmt(s, nxt):
        t = s.pk(); g = s.g
        if t[1] == '{' and t[0] == 'op':
            s.nx(); body = s.seq(); s.expect('}'); return A('block', body, line=t[2])
        if t[1] == 'if' and t[0] == 'kw':
            s.nx(); s.expect('(')
            if s.mode == 'sdt':
                lt, lf = g.label(), g.label(); s.cond(lt, lf); s.expect(')')
                g.place(lt); s.stmt(nxt); s.expect('else'); g.emit("goto %s" % g.jump(nxt)); g.place(lf); s.stmt(nxt); return None
            c = s.cond(None, None); s.expect(')'); a = s.stmt(None); s.expect('else'); b = s.stmt(None)
            return A('if', [c, a, b], line=t[2])
        if t[1] == 'while' and t[0] == 'kw':
            s.nx(); s.expect('(')
            if s.mode == 'sdt':
                begin, lt = g.label(), g.label(); g.place(begin); s.cond(lt, nxt); s.expect(')'); g.place(lt)
                s.stmt(begin); g.emit("goto %s" % g.jump(begin)); return None
            c = s.cond(None, None); s.expect(')'); return A('while', [c, s.stmt(None)], line=t[2])
        if t[0] == 'id':
            s.nx(); s.expect('='); e = s.expr(); s.expect(';'); s.consumed = True
            if s.mode == 'sdt':
                if t[1] not in s.sym: raise CompileError(t[2], "undeclared variable '%s'" % t[1])
                g.assign(t[1], s.sym[t[1]], e, t[2]); return None
            return A('assign', [e], t[1], t[2])
        raise CompileError(t[2], "syntax error: unexpected '%s'" % t[1])
    def seq(s):
        out = []
        while s.pk()[0] != 'eof' and not s.is_('}'):
            mark = len(s.g.code); nxt = s.g.label() if s.mode == 'sdt' else None; s.consumed = False
            try:
                node = s.stmt(nxt)
                if s.mode == 'sdt': s.g.place_if_used(nxt)
                else: out.append(node)
            except CompileError as e:
                s.errors.append(str(e)); del s.g.code[mark:]
                if not s.consumed: s.sync()
        return out
    def run(s):
        s.decls(); body = s.seq()
        if s.pk()[0] != 'eof':
            s.errors.append(str(CompileError(s.pk()[2], "syntax error: unexpected '%s'" % s.pk()[1])))
        if s.mode == 'ast': s.ast = body
        return s

def gen_pass(prog, sym, errors):
    """second pass of the baseline: walk the AST, type-check and generate the same TAC"""
    g = Gen()
    def ex(n):
        if n.k == 'num': n.ty = 'float' if '.' in n.v else 'int'; n.addr = n.v; return (n.v, n.ty)
        if n.k == 'id':
            if n.v not in sym: raise CompileError(n.line, "undeclared variable '%s'" % n.v)
            n.ty = sym[n.v]; n.addr = n.v; return (n.v, n.ty)
        x, y = ex(n.kids[0]), ex(n.kids[1]); r = g.binop(n.v, x, y); n.addr, n.ty = r; return r
    def st(n, nxt):
        if n.k == 'assign':
            e = ex(n.kids[0])
            if n.v not in sym: raise CompileError(n.line, "undeclared variable '%s'" % n.v)
            g.assign(n.v, sym[n.v], e, n.line); n.ty = sym[n.v]
        elif n.k == 'block': sq(n.kids)
        elif n.k == 'if':
            lt, lf = g.label(), g.label(); c = n.kids[0]
            g.relop(c.v, ex(c.kids[0]), ex(c.kids[1]), lt, lf); g.place(lt); st(n.kids[1], nxt)
            g.emit("goto %s" % g.jump(nxt)); g.place(lf); st(n.kids[2], nxt)
        elif n.k == 'while':
            begin, lt = g.label(), g.label(); c = n.kids[0]; g.place(begin)
            g.relop(c.v, ex(c.kids[0]), ex(c.kids[1]), lt, nxt); g.place(lt); st(n.kids[1], begin); g.emit("goto %s" % g.jump(begin))
    def sq(lst):
        for n in lst:
            mark = len(g.code); nxt = g.label()
            try: st(n, nxt); g.place_if_used(nxt)
            except CompileError as e: errors.append(str(e)); del g.code[mark:]
    sq(prog); return g.code

def translate(src, mode):
    p = MiniLang(src, mode).run()
    if mode == 'sdt': return p.g.code, p.errors, p.sym, p
    errs = list(p.errors); code = gen_pass(p.ast, p.sym, errs)
    return code, errs, p.sym, p

def ast_outline(nodes, d=0):
    out = []
    for n in nodes:
        a = "" if n.ty is None else "  [type=%s]" % n.ty
        lab = {'assign': "assign %s" % n.v, 'bin': "bin '%s'" % n.v, 'rel': "rel '%s'" % n.v, 'num': "num %s" % n.v,
               'id': "id %s" % n.v}.get(n.k, n.k)
        if n.addr is not None and n.k in ('bin', 'num', 'id'): a += "  [addr=%s]" % n.addr
        out.append((d, lab + a)); out += ast_outline(n.kids, d + 1)
    return out

SAMPLE = """int a, b, i;
float x, y;
a = 5;
b = a * 2 + 3;
x = (a + b) / 2;
if (a < b) y = x * 2.5; else y = x - 1;
while (i < 10) { i = i + 1; a = a + i; }
x = x + a;
"""

def make_prog(n):
    lines = ["int a, b, c;", "float x;"]
    for k in range(n):
        lines.append(["a = a + b * 2 - 1;", "c = (a - b) * (c + 3) / 2;", "x = x + a * 1.5;", "if (a < b) c = c + 1; else c = c - 1;"][k % 4])
    return "\n".join(lines)

def timing():
    rows = []
    for n in (250, 500, 1000, 2000, 4000, 8000):
        src = make_prog(n); ntok = len(lex(src))
        def best(mode):
            b = 1e9
            for _ in range(3):
                t = time.perf_counter(); translate(src, mode); b = min(b, time.perf_counter() - t)
            return b * 1000
        ts, ta = best('sdt'), best('ast')
        c1 = translate(src, 'sdt')[0]; c2 = translate(src, 'ast')[0]
        rows.append((n, ntok, len(c1), round(ts, 1), round(ta, 1), c1 == c2, round(ts * 1000 / ntok, 2), round(ta * 1000 / ntok, 2)))
    return rows

ERR_TESTS = [
    ("undeclared variable", "int a;\na = 1;\nb = a + 2;\na = a + 1;"),
    ("duplicate declaration", "int a, b, a;\na = 1;"),
    ("type error (float to int)", "int a;\nfloat x;\nx = 2.5;\na = x * 2;\nx = a;"),
    ("syntax error with recovery", "int a;\na = ;\na = 3;"),
    ("nested if/while", "int a, i;\nwhile (i < 3) { if (i < 2) a = a + 1; else { while (a > 0) a = a - 1; } i = i + 1; }"),
]

if __name__ == "__main__":
    for r in q1_tests(): print(r)
    rows, nest = height_experiment(); print(rows, nest, assoc_demo())
    for r in q2_tests(): print(r['src'], r['ok'], r.get('err'), r['table'])
    print(q4_tests()); print(q5_counts()); print(q5_memory())
    print(q6_tac("x = a + b * c - d")); print(q6_tac("x = a + b * c - d", True))
    for l in marker_trace(): print(l)
    c, e, s, p = translate(SAMPLE, 'sdt'); print("\n".join(c)); print(e, s)
    print(timing())
    for name, src in ERR_TESTS:
        c, e, s, p = translate(src, 'sdt'); c2, e2, _, _ = translate(src, 'ast')
        print(name, e, sorted(e) == sorted(e2), c == c2)
