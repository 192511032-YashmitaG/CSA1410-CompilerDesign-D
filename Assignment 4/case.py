"""Task 4: switch dispatch strategies and validation."""
import math
class SwitchError(ValueError): pass
class SwitchTranslator:
    def __init__(self,cases,default=None):
        self.cases=dict(cases); self.default=default
        if len(self.cases)!=len(cases): raise SwitchError('duplicate case label')
        self.keys=sorted(self.cases)
    def validate(self):
        if self.default is None: raise SwitchError('missing default clause')
    def sequential(self,value):
        tests=[]
        for k in self.keys:
            tests.append(f'if x == {k} goto L{k}')
            if value==k: return tests,self.cases[k],len(tests)
        tests.append('goto Ldefault'); return tests,self.default,len(self.keys)
    def binary(self,value):
        lo,hi=0,len(self.keys)-1; tests=[]
        while lo<=hi:
            mid=(lo+hi)//2; k=self.keys[mid]; tests.append(f'compare x with {k}')
            if value==k: return tests,self.cases[k],len(tests)
            if value<k: hi=mid-1
            else: lo=mid+1
        return tests,self.default,len(tests)
    def jump_table(self,value):
        if not self.keys: return ['goto Ldefault'],self.default,1,0
        low,high=self.keys[0],self.keys[-1]; size=high-low+1
        target=self.cases.get(value,self.default)
        return [f'index = x - ({low})',f'if index outside [0,{size-1}] goto Ldefault','goto table[index]'],target,2,size
    def demo(self):
        for v in (self.keys[0],self.keys[len(self.keys)//2],self.keys[-1],999):
            a=self.sequential(v); b=self.binary(v); c=self.jump_table(v)
            print(f'value={v}: sequential={a[2]} tests, binary={b[2]} tests, jump-table={c[2]} tests, slots={c[3]}')
        print('SEQUENTIAL',self.sequential(999)[0]); print('BINARY',self.binary(999)[0]); print('JUMP TABLE',self.jump_table(999)[0])
def demo(): SwitchTranslator({1:'one',2:'two',3:'three',1000:'big'},'default').demo()
