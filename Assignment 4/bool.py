"""Task 3: short-circuit Boolean control-flow skeleton with backpatch traces."""
from ir import Emitter
class BooleanTranslator:
    def __init__(self): self.ir=Emitter(); self.lists={}; self.trace=[]
    def relation(self,left,op,right):
        t=self.ir.emit('ifgoto',f'{left} {op} {right}',None,None); f=self.ir.emit('goto',None,None,None)
        return {'truelist':[t],'falselist':[f],'nextlist':[]}
    def and_expr(self,left,right_builder):
        m=len(self.ir.code); self.ir.backpatch(left['truelist'],m); right=right_builder()
        return {'truelist':right['truelist'],'falselist':self.ir.merge(left['falselist'],right['falselist']),'nextlist':[]}
    def or_expr(self,left,right_builder):
        m=len(self.ir.code); self.ir.backpatch(left['falselist'],m); right=right_builder()
        return {'truelist':self.ir.merge(left['truelist'],right['truelist']),'falselist':right['falselist'],'nextlist':[]}
    def finish(self,expr):
        end=len(self.ir.code); self.ir.backpatch(expr['truelist'],end); self.ir.backpatch(expr['falselist'],end)
        self.ir.emit('label',None,None,end); return self.ir.check()
    def demo(self):
        e=self.relation('a','<','b'); e=self.and_expr(e,lambda:self.relation('c','<','d'))
        print('LISTS',e); print('FINAL QUADRUPLES'); self.ir.show(); print('CHECK',self.ir.check())
        bad=Emitter(); bad.emit('goto',None,None,None); print('DELIBERATE DEFECT',bad.check())
def demo(): BooleanTranslator().demo()
