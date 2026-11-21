"""Task 2/3: intermediate representation and backpatching primitives."""
from dataclasses import dataclass
@dataclass
class Quad:
    op:str; arg1:object=None; arg2:object=None; result:object=None
    def __str__(self): return f'({self.op}, {self.arg1}, {self.arg2}, {self.result})'
class Emitter:
    def __init__(self): self.code=[]
    def emit(self,op,a=None,b=None,r=None): self.code.append(Quad(op,a,b,r)); return len(self.code)-1
    def makelist(self,i): return [i]
    def merge(self,*lists): return [x for xs in lists for x in xs]
    def backpatch(self,items,target):
        for i in items:
            if not 0<=i<len(self.code): raise IndexError(f'invalid instruction {i}')
            self.code[i].result=target
    def check(self):
        errors=[]
        for i,q in enumerate(self.code):
            if q.op in ('goto','ifgoto') and (not isinstance(q.result,int) or not 0<=q.result<len(self.code)):
                errors.append(f'quad {i}: unresolved/out-of-range target {q.result}')
        return errors
    def show(self):
        for i,q in enumerate(self.code): print(f'{i:03}: {q}')
    def triples(self): return [(q.op,q.arg1,q.arg2) for q in self.code]
    def indirect(self): return list(range(len(self.code))),self.triples()
