"""Task 5: argument queue, call sequence and activation record layout."""
class CallGenerator:
    def __init__(self): self.code=[]; self.queue=[]
    def arg(self,value): self.queue.append(value); self.code.append(f'arg {value}')
    def call(self,name,n,result=None):
        if n>len(self.queue): raise ValueError('argument queue underflow')
        args=self.queue[-n:] if n else [];
        if n: del self.queue[-n:]
        self.code.append(f'call {name}, {n}')
        if result: self.code.append(f'{result} = RET')
        return args
    def frame(self,params,locals_,temps,word=8):
        rows=[]; off=0
        for kind,names,w in [('parameter',params,word),('local',locals_,word),('temporary',temps,word)]:
            for name in names: rows.append((name,kind,off,w)); off+=w
        rows += [('retval','return value',off,word),('retaddr','return address',off+word,4),('dynlink','saved frame ptr',off+word+4,4)]
        return rows
    def demo(self):
        self.arg('n'); self.arg('n-1'); self.call('fact',2,'t1'); self.code.append('return t1')
        print('\n'.join(self.code)); print('ACTIVATION RECORD')
        for r in self.frame(['a','b'],['loc1','loc2'],['t1','t2','t3']): print(r)
def demo(): CallGenerator().demo()
