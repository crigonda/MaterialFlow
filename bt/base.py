"""Nodes."""
from abc import ABCMeta, abstractmethod

class Task(object, metaclass=ABCMeta):
    """ Classe base pour un noeud du Behavior Tree """
    ECHEC, SUCCES, RUNNING = range(3)  # compatibilite: False est un ECHEC et True est un SUCCES

    def __init__(self):
        self._children = []
        self.index = 0

    @abstractmethod
    def run(self):
        """Ticks."""
        return

    def add_child(self, c):
        """Adds a child."""
        self._children.append(c)

class Decorator(Task):
    """ Decorator """
    __metaclass__ = ABCMeta

    def __init__(self):
        super().__init__()

    def add_child(self, c):
        if len(self._children) < 1:
            super(Decorator, self).add_child(c)


class Selector(Task):
    """ Selector """

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(self.index, len(self._children)):
            status = self._children[i].run()
            if status == Task.SUCCES:
                return Task.SUCCES
            elif status == Task.RUNNING:
                return Task.RUNNING
        return Task.ECHEC

    def add_child(self, c):
        super(Selector, self).add_child(c)


class SelectorStar(Task):
    """ Selector star """

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(self.index, len(self._children)):
            status = self._children[i].run()
            if status == Task.SUCCES:
                self.index = 0
                return Task.SUCCES
            elif status == Task.RUNNING:
                self.index = i
                return Task.RUNNING
        self.index = 0
        return Task.ECHEC

    def add_child(self, c):
        super(SelectorStar, self).add_child(c)


class Sequence(Task):
    """ Sequence """

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(self.index, len(self._children)):
            status = self._children[i].run()
            if status == Task.ECHEC:
                return Task.ECHEC
            elif status == Task.RUNNING:
                return Task.RUNNING
        return Task.SUCCES

    def add_child(self, c):
        super().add_child(c)


class SequenceStar(Task):
    """ Sequence star """

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(self.index, len(self._children)):
            status = self._children[i].run()
            if status == Task.ECHEC:
                self.index = 0
                return Task.ECHEC
            elif status == Task.RUNNING:
                self.index = i
                return Task.RUNNING
        self.index = 0
        return Task.SUCCES

    def add_child(self, c):
        super().add_child(c)

# ==================================================================================================

class NodeTask(Task):
    """Model related task."""
    def __init__(self, node):
        super().__init__()
        self.node = node

    @abstractmethod
    def run(self):
        """Ticks."""
        return

class Threshold(Task):
    """Threshold condition Task."""
    # Comparison type
    INFERIOR, SUPERIOR = range(2)

    def __init__(self, element, threshold, comp=SUPERIOR):
        super().__init__()
        self.element = element
        self.threshold = threshold
        if comp == Threshold.INFERIOR:
            self.cond = self._inf
        else:
            self.cond = self._sup

    def _inf(self):
        """Inferior."""
        if self.element.current <= self.threshold:
            return Task.SUCCES
        else:
            return Task.ECHEC

    def _sup(self):
        """Superior."""
        if self.element.current >= self.threshold:
            return Task.SUCCES
        else:
            return Task.ECHEC

    def run(self):
        return self.cond()

class SpaceChecker(Task):
    """Verifies the remaining space in a model element."""
    def __init__(self, element, minSpace):
        super().__init__()
        # Element
        self.element = element
        # The minimum space
        self.minSpace = minSpace

    def run(self):
        # Does the element has the required space ?
        if self.element.capacity - self.element.current >= self.minSpace:
            return Task.SUCCES
        else:
            return Task.ECHEC

class RawUpdater(Task):
    """Updates the value of an element."""
    def __init__(self, elementFrom, elementTo, value):
        super().__init__()
        self.elementFrom = elementFrom
        self.elementTo = elementTo
        self.value = value

    def run(self):
        if self.elementTo.increase(self.value):
            self.elementFrom.decrease(self.value)
            return Task.SUCCES
        return Task.ECHEC

class Mine(NodeTask):
    """Generates iron ore over a given period."""
    def __init__(self, node, outEdge, genFunc, nbTicks, minUpdate):
        super().__init__(node)
        # Outgoing edge
        self.outEdge = outEdge
        # Generation function
        self.genFunc = genFunc
        # Number of ticks in the period
        self.nbTicks = nbTicks
        # The minimum amount to produce in the node before updating the outgoing edge
        self.minUpdate = minUpdate
        # Remaining number of ticks
        self.remaining = nbTicks
        # Amount to produce at each tick over the current period
        self.tickAmount = self.genFunc()/nbTicks

    def run(self):
        # If the production period is over
        if self.remaining == 0:
            self.remaining = self.nbTicks
            self.tickAmount = self.genFunc()/self.nbTicks
        # Increases node value if possible
        running = self.node.increase(self.tickAmount)
        # Updates outgoing edge if possible
        if self.node.current >= self.minUpdate:
            if self.outEdge.increase(self.minUpdate):
                self.node.decrease(self.minUpdate)
        # Decreases counter
        self.remaining -= 1
        # Returns running if the mine can still produce iron
        return Task.RUNNING if running else Task.ECHEC

class Train(NodeTask):
    """Brings chemical products."""
    def __init__(self, node, outEdge, nbWagons, wagonCapacity):
        super().__init__(node)
        # Outgoing edge
        self.outEdge = outEdge
        # Number of wagons
        self.nbWagons = nbWagons
        # Capacity (litres) of a wagon
        self.wagonCapacity = wagonCapacity

    def run(self):
        # Increases the outgoing edge value
        success = self.outEdge.increase(self.nbWagons*self.wagonCapacity)
        return Task.SUCCES if success else Task.ECHEC

class Boat(NodeTask):
    """The boat leaves after loading."""
    def __init__(self, node, incEdge, boatSize):
        super().__init__(node)
        # Incoming edge
        self.incEdge = incEdge
        # Boat size
        self.boatSize = boatSize

    def run(self):
         # Decreases the incoming edge value
        success = self.incEdge.decrease(self.boatSize)
        return Task.SUCCES if success else Task.ECHEC

class Consume(NodeTask):
    """Decreases the incoming edge, increases node and outgoing edge."""
    def __init__(self, incEdge, node, outEdge, toProduce, incStep, nodeStep, minUpdate):
        # Node
        super().__init__(node)
        # Total production to achieve
        self.toProduce = toProduce
        # Remaining production
        self.remaining = toProduce
        # Incoming edge
        self.incEdge = incEdge
        # Outgoing edge
        self.outEdge = outEdge
        # The amount by which the incoming edge is to be decreased
        self.incStep = incStep
        # The amount by which the node and the outgoing edge are to be increased
        self.nodeStep = nodeStep
        # The minimum amount to produce in the node before updating the outgoing edge
        self.minUpdate = minUpdate

    def run(self):
        # Decreases value of incoming edge
        self.incEdge.decrease(self.incStep)
        # Increases node value, decreases remaining amount
        self.node.increase(self.nodeStep)
        self.remaining -= self.nodeStep
        # If a minimum threshold has been produced
        if self.node.current >= self.minUpdate:
            # Increases outgoing edge
            if self.outEdge.increase(self.nodeStep):
                # Decreases node
                self.node.decrease(self.nodeStep)
        # If the production is finished, returns FINISHED
        if self.remaining < self.nodeStep:
            self.remaining = self.toProduce
            # Empty the node
            leftovers = self.node.current
            if leftovers <= self.minUpdate:
                self.node.decrease(leftovers)
                self.outEdge.increase(leftovers)
            return Task.SUCCES
        # Else, returns RUNNING
        else:
            return Task.RUNNING

class MultipleConsume(NodeTask):
    """Decreases the incoming edges, increases node and outgoing edge."""
    def __init__(self, incEdges, node, outEdge, toProduce, incSteps, nodeStep, minUpdate):
        # Node
        super().__init__(node)
        # Total production to achieve
        self.toProduce = toProduce
        # Remaining production
        self.remaining = toProduce
        # Incoming edges
        self.incEdges = incEdges
        # Outgoing edge
        self.outEdge = outEdge
        # The amount by which the incoming edges are to be decreased
        self.incSteps = incSteps
        # The amount by which the node and the outgoing edge are to be increased
        self.nodeStep = nodeStep
        # The minimum amount to produce in the node before updating the outgoing edge
        self.minUpdate = minUpdate

    def run(self):
        # Decreases value of incoming edges
        for index, edge in enumerate(self.incEdges):
            edge.decrease(self.incSteps[index])
        # Increases node value, decreases remaining amount
        self.node.increase(self.nodeStep)
        self.remaining -= self.nodeStep
        # If a minimum threshold has been produced
        if self.node.current >= self.minUpdate:
            # Increases outgoing edge
            if self.outEdge.increase(self.nodeStep):
                # Decreases node
                self.node.decrease(self.nodeStep)
        # If the production is finished, returns FINISHED
        if self.remaining < self.nodeStep:
            self.remaining = self.toProduce
            # Empty the node
            leftovers = self.node.current
            if leftovers <= self.minUpdate:
                self.node.decrease(leftovers)
                self.outEdge.increase(leftovers)
            return Task.SUCCES
        # Else, returns RUNNING
        else:
            return Task.RUNNING
