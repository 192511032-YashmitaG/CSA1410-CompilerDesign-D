"""Re-definition-aware DAG and local expression simplification."""
def optimise_block(statements):
    current={}
    output=[]
    expr={}
    def resolve(x):
        return current.get(x, x)
    for dst, op, a, b in statements:
        x,y=resolve(a),resolve(b)
        if op=="mul" and y==1: value=x
        elif op=="mul" and x==1: value=y
        elif op=="add" and y==0: value=x
        elif op=="add" and x==0: value=y
        elif isinstance(x,int) and isinstance(y,int):
            value={"add":lambda:x+y,"sub":lambda:x-y,"mul":lambda:x*y,"div":lambda:x//y}[op]()
        else:
            key=(op,x,y) if op in ("add","mul") else (op,x,y)
            if op in ("add","mul") and repr(x)>repr(y): key=(op,y,x)
            if key in expr: value=expr[key]
            else:
                value=f"v{len(expr)+1}"; expr[key]=value
                output.append((value,op,x,y))
        current[dst]=value
    # Keep only computed values that feed a named final value.
    return output, current

def peephole(lines):
    out=[]
    for line in lines:
        if out and out[-1].startswith("ST ") and line.startswith("LD "):
            st=out[-1].replace("ST ","").replace(", "," ")
            ld=line.replace("LD ","").replace(", "," ")
            if st.split()[0]==ld.split()[-1]:
                out.pop(); continue
        out.append(line)
    return out
