"""Task 2: three-address expression translator (Python expression syntax)."""
import ast
from ir import Emitter

class ExpressionGenerator:
    def __init__(self,types=None):
        self.types=types or {}; self.ir=Emitter(); self.temp=0; self.values={}; self.trace=[]
    def newtemp(self): self.temp+=1; t=f't{self.temp}'; self.trace.append(f'allocate {t}'); return t
    def gen(self,source,optimise=True):
        tree=ast.parse(source,mode='eval').body
        result,typ=self._node(tree,optimise)
        return result,typ
    def _node(self,n,opt):
        if isinstance(n,ast.Constant): return repr(n.value),('float' if isinstance(n.value,float) else 'int')
        if isinstance(n,ast.Name): return n.id,self.types.get(n.id,'int')
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):
            a,t=self._node(n.operand,opt); key=('neg',a,t)
            if opt and key in self.values: return self.values[key],t
            r=self.newtemp(); self.ir.emit('uminus',a,None,r); self.values[key]=r; return r,t
        if isinstance(n,ast.BinOp):
            a,ta=self._node(n.left,opt); b,tb=self._node(n.right,opt)
            if ta!=tb and {ta,tb}=={'int','float'}:
                if ta=='int': x=self.newtemp(); self.ir.emit('inttofloat',a,None,x); a=x
                if tb=='int': x=self.newtemp(); self.ir.emit('inttofloat',b,None,x); b=x
                typ='float'
            else: typ='float' if 'float' in (ta,tb) else 'int'
            op={ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/'}[type(n.op)]
            key=(op,a,b,typ)
            if opt and key in self.values: self.trace.append(f'value-number hit {key}'); return self.values[key],typ
            r=self.newtemp(); self.ir.emit(op,a,b,r); self.values[key]=r; return r,typ
        if isinstance(n,ast.Subscript):
            base,_=self._node(n.value,opt); idx,_=self._node(n.slice,opt); r=self.newtemp(); self.ir.emit('bounds_check',idx,base,None); self.ir.emit('load_index',base,idx,r); return r,self.types.get(base,'int')
        raise ValueError(f'unsupported expression: {ast.dump(n)}')
    def assignment(self,lhs,rhs,optimise=True):
        val,typ=self.gen(rhs,optimise); self.ir.emit('=',val,None,lhs); return val,typ
    def display(self):
        print('QUADRUPLES'); self.ir.show(); print('TRIPLES');
        for i,x in enumerate(self.ir.triples()): print(i,x)
        order,triples=self.ir.indirect(); print('INDIRECT TRIPLES',order,triples); print('TEMPORARIES',self.temp); print('TRACE',self.trace)

def demo():
    g=ExpressionGenerator({'a':'int','b':'int','A':'float','i':'int','j':'int'})
    g.assignment('x','(a+b)*(a+b) + A[i][j]*2.0'); g.display()
