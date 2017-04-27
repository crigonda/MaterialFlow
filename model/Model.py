"""Objects of the model."""

from enum import Enum
from math import atan2, fabs, pi
from copy import deepcopy
from tkinter import LAST
import queue

# Walk type
class NodeState(Enum):
    """WORKING - WAITING"""
    WORKING = 1 ; WAITING = 2

def trunc(number):
    """Truncates to 3 decimals."""
    if number == "":
        return ""
    return '%.3f'%number

class ModelObject(object):
    """Object of the model."""
    def __init__(self, name, capacity):
        self.name = name
        # Current stock in the element
        self.current = 0
        self.capacity = capacity

    def increase(self, amount):
        """Increases the current value of the object from a given amount."""
        if self.current + amount <= self.capacity:
            self.current += amount
            return True
        else:
            return False

    def decrease(self, amount):
        """Decreases the current value of the object from a given amount."""
        if self.current - amount >= 0:
            self.current -= amount
            return True
        else:
            return False

    def draw(self, canvas, canvas_x, canvas_y):
        """Draws the object on a canvas."""
        raise NotImplementedError("draw method not implemented !")

    def __str__(self):
        """String representation."""
        return "N: " + self.name + ";C:" + self.capacity

    def __repr__(self):
        return self.__str__()

class Node(ModelObject):
    """Node of the model."""
    def __init__(self, name, capacity, size=None, position=None, bTree=None):
        ModelObject.__init__(self, name, capacity)
        # Behaviour tree of the node
        self.bTree = bTree
        # List of incoming edges
        self.incoming = []
        # List of outgoing edges
        self.outgoing = []
        self.size = size
        self.position = position

    def run(self):
        """Ticks the node behaviour tree."""
        self.bTree.run()

    def draw(self, canvas, canvas_x, canvas_y):
        """Draws the node on a canvas."""
        # Draws a rectangle
        x = (self.position[0]/100)*canvas_x
        y = (self.position[1]/100)*canvas_y
        dx = ((self.size[0]/2)/100)*canvas_x
        dy = ((self.size[1]/2)/100)*canvas_y
        canvas.create_rectangle(x-dx, y+dy, x+dx, y-dy, fill='pale green')
        # Adds the name
        canvas.create_text(x, y, text=self.name)
        # Adds the capacity
        canvas.create_text(x, y+dy/2, text=str(trunc(self.current))+"/"+str(self.capacity))

class Edge(ModelObject):
    """Edge of the model."""
    def __init__(self, name, capacity):
        ModelObject.__init__(self, name, capacity)
        # Origin node of the edge
        self.nodeFrom = None
        # Destination node of the edge
        self.nodeTo = None

    def draw(self, canvas, canvas_x, canvas_y):
        """Draws the edge on a canvas."""
        xFrom = (self.nodeFrom.position[0]/100)*canvas_x
        yFrom = (self.nodeFrom.position[1]/100)*canvas_y
        xTo = (self.nodeTo.position[0]/100)*canvas_x
        yTo = (self.nodeTo.position[1]/100)*canvas_y
        dxFrom = ((self.nodeFrom.size[0]/2)/100)*canvas_x
        dyFrom = ((self.nodeFrom.size[1]/2)/100)*canvas_y
        dxTo = ((self.nodeTo.size[0]/2)/100)*canvas_x
        dyTo = ((self.nodeTo.size[1]/2)/100)*canvas_y
        vect = (xTo-xFrom, yTo-yFrom)
        angle = atan2(vect[1], vect[0])*(180/pi)
        # Right dial
        if fabs(angle) <= 45:
            xFrom += dxFrom
            xTo -= dxTo
        # Left dial
        elif fabs(angle) >= 135:
            xFrom -= dxFrom
            xTo += dxTo
        # Upper dial
        elif angle > 0:
            yFrom += dyFrom
            yTo -= dyTo
        # Lower dial
        elif angle < 0:
            yFrom -= dyFrom
            yTo += dyTo
        else:
            print("Unexpected case.")
        # Creates a line
        canvas.create_line(xFrom, yFrom, xTo, yTo, arrow=LAST)
        # Adds text
        canvas.create_text((xFrom+xTo)/2, (yFrom+yTo)/2+10,\
        text=self.name+": "+str(trunc(self.current))+"/"+str(self.capacity))

class Model(object):
    """Model."""
    def __init__(self, gui=None):
        self.nodes = []
        self.edges = []
        self.gui = gui

    def addNode(self, name, capacity, size=None, position=None, bTree=None):
        """Adds a node to the model.
        Returns the node and its index in the node list."""
        # Adds the node to the list
        node = Node(name, capacity, size, position, bTree)
        self.nodes.append(node)
        return (node, len(self.nodes)-1)

    def addEdge(self, name, capacity, iNodeFrom, iNodeTo):
        """Adds an edge between two nodes (from their indexes) in the model.
        Returns the index of the edge in the edge list."""
        edge = Edge(name, capacity)
        nodeFrom = self.nodes[iNodeFrom]
        nodeTo = self.nodes[iNodeTo]
        # Links the edge to the nodes
        edge.nodeFrom = nodeFrom
        edge.nodeTo = nodeTo
        # Adds the edge in the nodes lists
        nodeFrom.outgoing.append(edge)
        nodeTo.incoming.append(edge)
        # Adds the edge to the list
        self.edges.append(edge)
        return (edge, len(self.edges)-1)

    def run(self):
        """Runs the model."""
        # Ticks all the nodes behaviour trees
        for node in self.nodes:
            if node.bTree is not None:
                node.bTree.run()
        self.notifyGUI()

    def notifyGUI(self):
        """Notifies the GUI of the changes to the model."""
        try:
            self.gui.put((deepcopy(self.nodes), deepcopy(self.edges)))
        except queue.Full:
            print("Queue is full !!")
