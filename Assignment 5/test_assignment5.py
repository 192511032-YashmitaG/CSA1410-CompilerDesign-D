import unittest
from ir import Instr, leaders, partition, flow_graph, next_use
from dag import optimise_block, peephole
from dataflow import liveness, reaching_definitions
from codegen import Generator

class Assignment5Tests(unittest.TestCase):
    def test_leaders_and_partition(self):
        code=[Instr("copy","x","1"),Instr("if",a="x",b="0",target=3),
              Instr("copy","y","2"),Instr("goto",target=0)]
        self.assertEqual(leaders(code),[0,2,3])
        self.assertEqual(len(partition(code)),3)
    def test_flow_graph(self):
        blocks,succ,pred=flow_graph([Instr("goto",target=1),Instr("copy","x","1")])
        self.assertEqual(succ[0],[1]); self.assertEqual(pred[1],[0])
    def test_next_use(self):
        code=[Instr("bin","t","x","y"),Instr("bin","z","t","x")]
        n=next_use([0,1],code,{"z"})
        self.assertIn("x",n[0])
    def test_dag_identity(self):
        out,vals=optimise_block([("t","mul","x",1),("z","add","t",0)])
        self.assertEqual(vals["z"],"x")
        self.assertEqual(out,[])
    def test_register_codegen(self):
        g=Generator(2); code=g.generate([("t","add","a","b"),("z","add","t","c")])
        self.assertTrue(code); self.assertGreaterEqual(g.cost,1)
    def test_liveness_fixed_point(self):
        inn,out,visits=liveness({0:[1],1:[]},[{"a"},{"b"}],[{"b"},{"c"}])
        self.assertIn("a",inn[0]); self.assertGreater(visits,0)

if __name__=="__main__": unittest.main()
