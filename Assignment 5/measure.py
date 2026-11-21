"""Reproducible measurements for register pressure and data-flow work."""
from codegen import Generator

def run():
    ir=[("t1","sub","a","b"),("t2","sub","a","c"),
        ("t3","add","t1","t2"),("d","add","t3","t2")]
    print("k,strategy,instructions,loads,stores,spills,cost")
    for k in (2,3,4,8):
        for strategy in ("first","next_use"):
            g=Generator(k,strategy); g.generate(ir)
            print(k,strategy,len(g.code),g.loads,g.stores,g.spills,g.cost)
if __name__=="__main__": run()
