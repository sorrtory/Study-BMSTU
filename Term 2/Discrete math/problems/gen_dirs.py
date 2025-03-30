import os

m1 = "utf8 add gaus polish econom arith m1-exam".split()
m2 = "Dividers Mars MaxComponent BridgeNum EqDist Kruskal Prim GraphBase Modules Cpm Loops FormulaOrder MapRoute m2-exam".split()
m3 = "Canonic VisMealy LangMealy MinMealy EqMealy Mealy2Moore DetRec m3-exam".split()

l = [m1, m2, m3]

pattern = '''\
package main

import (
    "fmt"
)

func main() {
    fmt.Print()
}
'''

for i, module in enumerate(l):
    dName = "module"+str(i+1)
    os.mkdir(dName)
    for j, taskName in enumerate(module):
        os.mkdir(f"{dName}/{j+1}) {taskName}")
        with open(f"{dName}/{j+1}) {taskName}/{taskName}.go", "w") as f:
            f.write(pattern)
        