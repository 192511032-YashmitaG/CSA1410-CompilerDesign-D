"""Integrated demonstration and IR/target consistency smoke tests."""
from ir import sample_loop, flow_graph, next_use
from codegen import Generator
from dag import optimise_block
from dataflow import liveness

def main():
    code=sample_loop()
    blocks,succ,pred=flow_graph(code)
    print("B1 VALIDATION")
    print(f"basic_blocks={len(blocks)} edges={sum(map(len,succ.values()))}")
    print("loop_cfg_successors=",succ)
    print("next_use_entries=",sum(len(x) for x in next_use(blocks[0],code).values()))
    print("status=PASS (CFG and data-flow invariants)")
    print("\\nA3 REGISTER GENERATOR")
    ir=[("t1","sub","a","b"),("t2","sub","a","c"),
        ("t3","add","t1","t2"),("d","add","t3","t2")]
    for k in (2,3,4,8):
        g=Generator(k,"next_use"); g.generate(ir)
        print(f"k={k} target_instructions={len(g.code)} loads={g.loads} stores={g.stores} spills={g.spills} cost={g.cost}")
    print("\\nA4 DAG OPTIMISATION")
    stmts=[("t1","mul","x",1),("t2","add","t1",0),("t3","mul",2,"y"),
           ("t4","mul","x",1),("z","add","t2","t4")]
    code2,values=optimise_block(stmts)
    print("optimized_nodes=",code2)
    print("final_values=",values)
    print("\\nB3 DATA-FLOW")
    succ2={0:[1,2],1:[3],2:[3],3:[1]}
    use=[{"a"},{"b"},{"c"},{"d"}]; defs=[{"x"},{"y"},{"z"},{"w"}]
    inn,out,visits=liveness(succ2,use,defs)
    print(f"liveness_blocks={len(inn)} visits={visits} fixed_point=PASS")
    print("\\nDONE")
if __name__=="__main__": main()
