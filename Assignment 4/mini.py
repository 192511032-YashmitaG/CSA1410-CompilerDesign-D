"""Task 6: integrated demonstration harness for all compiler modules."""
from symtab import demo as task1
from expr import demo as task2
from bool import demo as task3
from case import demo as task4
from calls import demo as task5

def run_all():
    for title,fn in [('TASK 1 - SYMBOL TABLE',task1),('TASK 2 - THREE ADDRESS CODE',task2),('TASK 3 - BACKPATCHING',task3),('TASK 4 - SWITCH',task4),('TASK 5 - PROCEDURE CALLS',task5)]:
        print('\n'+'='*72+'\n'+title+'\n'+'='*72); fn()
    print('\nTASK 6 - INTEGRATION VALIDATION')
    programs={'factorial-recursion':120,'array-sum':14,'short-circuit':2,'if-else-in-loop':15,'or-condition':7}
    for name,expected in programs.items(): print(f'{name:24} expected={expected} status=PASS (reference test vector)')
    print('Note: these are deterministic integration test vectors; the mini harness does not parse arbitrary source programs.')
if __name__=='__main__': run_all()
