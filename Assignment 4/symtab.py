"""Task 1: declaration processor with nested scopes and layout tracing."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Type:
    kind: str
    width: int
    element: 'Type|None' = None
    count: int = 0
    fields: tuple = ()
    def __str__(self):
        if self.kind == 'array': return f'array({self.count}, {self.element})'
        if self.kind == 'pointer': return f'pointer({self.element})'
        if self.kind == 'record': return 'record{' + ', '.join(f'{n}:{t}' for n,t,_ in self.fields) + '}'
        return self.kind

class DeclarationError(ValueError): pass

class SymbolTable:
    def __init__(self, widths=None, alignment=1, record_alignment=1):
        self.widths = {'int':4,'float':8,'boolean':1,'char':1,'pointer':4}
        if widths: self.widths.update(widths)
        self.alignment, self.record_alignment = alignment, record_alignment
        self.scopes=[{'name':'global','symbols':{},'offset':0}]
        self.trace=[]
    @property
    def scope(self): return self.scopes[-1]
    def enter_scope(self,name):
        self.scopes.append({'name':name,'symbols':{},'offset':0}); self.trace.append(f'enter_scope({name})')
    def leave_scope(self):
        if len(self.scopes)==1: raise DeclarationError('cannot leave global scope')
        s=self.scopes.pop(); self.trace.append(f'leave_scope({s["name"]}) total={s["offset"]}'); return s
    def _align(self,n,a): return (n+a-1)//a*a if a>1 else n
    def primitive(self,name):
        if name not in ('int','float','boolean','char'): raise DeclarationError(f"unknown type '{name}'")
        return Type(name,self.widths[name])
    def pointer(self,t): return Type('pointer',self.widths['pointer'],element=t)
    def array(self,count,t):
        if count<=0: raise DeclarationError('array size must be positive')
        return Type('array',count*t.width,element=t,count=count)
    def record(self,fields,name='record'):
        off=0; laid=[]
        for fname,ftype in fields:
            off=self._align(off,self.alignment); laid.append((fname,ftype,off)); off+=ftype.width
        width=self._align(off,self.record_alignment)
        self.trace.append(f'record {name}: width={width}, fields={[(n,str(t),o) for n,t,o in laid]}')
        return Type('record',width,fields=tuple(laid))
    def declare(self,name,t):
        s=self.scope
        if name in s['symbols']: raise DeclarationError(f"duplicate declaration of '{name}'")
        before=s['offset']; off=self._align(before,self.alignment)
        self.trace.append(f'enter({name}, t={t}, w={t.width})')
        if off!=before: self.trace.append(f'padding: offset {before} -> {off}')
        s['symbols'][name]={'name':name,'type':str(t),'width':t.width,'offset':off,'scope':s['name']}
        s['offset']=off+t.width; self.trace.append(f'offset update: {before} -> {s["offset"]}')
        return s['symbols'][name]
    def rows(self): return [v for s in self.scopes for v in s['symbols'].values()]
    def report(self):
        for r in self.rows(): print(f"{r['name']:<8} {r['type']:<28} width={r['width']:<4} offset={r['offset']:<4} scope={r['scope']}")
        for s in self.scopes: print(f"TOTAL {s['name']} = {s['offset']} bytes")
        print('TRACE:'); print('\n'.join(self.trace))

def demo():
    st=SymbolTable(); i=st.primitive('int'); f=st.primitive('float')
    st.declare('a',i); st.declare('b',i); st.declare('c',st.array(10,f))
    st.declare('r',st.record([('x',i),('y',f)],'R')); st.declare('p',st.pointer(f))
    st.report()
    try: st.declare('a',i)
    except DeclarationError as e: print('BOUNDARY:',e)
