from model.ModelBuilder import preparationBT
from model.Model import Node, Edge


CAPACITY = 1000000
# Nodes
node = Node("node", CAPACITY)
# Edges
incEdge = Edge("incEdge", CAPACITY)
outEdge = Edge("outEdge", CAPACITY)
incEdge.nodeTo = node
incEdge.current = CAPACITY
outEdge.nodeFrom = node
# Behaviour tree
node.bTree = preparationBT(incEdge, node, outEdge)
while True:
    ret = node.bTree.run()
    print(ret)
