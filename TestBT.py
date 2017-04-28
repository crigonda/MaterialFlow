from model.ModelBuilder import shipmentBT
from model.Model import Node, Edge

CAPACITY = 3000
# Nodes
node = Node("node", CAPACITY)
# Edges
incEdge = Edge("incEdge", CAPACITY)
outEdge = Edge("outEdge", CAPACITY)
incEdge.nodeTo = node
incEdge.current = 2000
outEdge.nodeFrom = node
# Behaviour tree
node.bTree = shipmentBT(incEdge, node, outEdge)
# while True:
#     ret = node.bTree.run()
#     print(ret)

count = 0
for i in range(1200):
    count+=1
    if i == 1198:
        print(count)
    ret = node.bTree.run()
    print(ret)
