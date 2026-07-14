from collections import defaultdict
from collections import Counter
from collections.abc import Iterator
import ast
dic = dict()
def abb(a, i=0):
    if i == len(a):
        return
    
    abb(a, i + 1)

a = input()
l = ast.literal_eval(a)
l1 = sorted(l, key = lambda x: len(x))
d = dict(Counter(l1))
keys = []
keys.append(len(abb(l1)))
print(keys)



