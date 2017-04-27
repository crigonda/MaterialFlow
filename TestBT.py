from model.ModelBuilder import receiptBT
from model.Model import Node, Edge


def trunc(number):
    """Truncates to 3 decimals."""
    return '%.3f'%float(number)
print(trunc(10.01223355))

CAPACITY = 360000
# Nodes
node = Node("node", CAPACITY)
# Edges
incEdge = Edge("incEdge", CAPACITY)
outEdge = Edge("outEdge", CAPACITY)
incEdge.nodeTo = node
incEdge.current = CAPACITY
outEdge.nodeFrom = node
# Behaviour tree
node.bTree = receiptBT(incEdge, node, outEdge)
# while True:
#     ret = node.bTree.run()
#     print(ret)

for i in range(2):
    for j in range(30):
        ret = node.bTree.run()
        print(ret)
    # Reloads edge
    incEdge.current = CAPACITY
