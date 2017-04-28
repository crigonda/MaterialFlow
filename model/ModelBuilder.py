"""Model builder : nodes, edges, behaviour trees."""

from random import random
from math import sqrt
from bt.base import Sequence, SequenceStar, SelectorStar, Threshold, SpaceChecker, RawUpdater
from bt.base import Consume, MultipleConsume, Mine, Train, Boat
from bt.decorator import Delay, Repeater, ThresholdDec
from .config import *


def triangularDistrib():
    """Generates a Triangular-distributed random variate."""
    MIN = 10 ; MAX = 60 ; MOD = 20
    rand = random()
    mid = (MOD-MIN)/(MAX-MIN)
    if rand < mid:
        return MIN + sqrt(rand*(MAX-MIN)*(MOD-MIN))
    else:
        return MAX - sqrt((1-rand)*(MAX-MIN)*(MAX-MOD))

# ========================================= BEHAVIOUR TREES ========================================
def trainBT(node, outEdge):
    """Train BT."""
    # We assume that the train always brings 2/3 solvent, 1/3 base
    # Waits a given amount of time between two trains
    wait = Delay(TRAIN_REFRESH_TIME)
    # Train brings in wagons with chemical products
    train = Train(node, outEdge, NB_WAGONS, WAGON_CAPACITY)
    wait.add_child(train)
    return wait

def miningBT(node, outEdge):
    """Mining BT."""
    nbTicks = MINE_REFRESH_TIME/TICK
    # Minimum to produce before updating the edge (ton)
    minUpdate = 1
    mine = Mine(node, outEdge, triangularDistrib, nbTicks, minUpdate)
    return mine

def boatBT(incEdge, node):
    """Boat BT."""
    seq = Sequence()
    # Verifies if the loading has been done
    verifyLoading = Threshold(incEdge, BOAT_CAPACITY, Threshold.SUPERIOR)
    seq.add_child(verifyLoading)
    # The boat leaves
    boat = Boat(node, incEdge, BOAT_CAPACITY)
    seq.add_child(boat)
    return boat

def consumer(incEdge, node, outEdge, quantity, incStep, nodeStep, minUpdate):
    """Consumer BT."""
    seqStar1 = SequenceStar()
    # Verifies if there is enough space in the outgoing edge
    outEdgeChecker = SpaceChecker(outEdge, quantity)
    seqStar1.add_child(outEdgeChecker)
    # Selects among one of the two following possibilities
    selectorStar = SelectorStar()
    seqStar1.add_child(selectorStar)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FIRST POSSIBILITY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Is there already material in the node ?
    nodeChecker = ThresholdDec(node, quantity)
    selectorStar.add_child(nodeChecker)
    # Updates the outgoing edge if it the case
    outEdgeUpdater = RawUpdater(node, outEdge, quantity)
    nodeChecker.add_child(outEdgeUpdater)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SECOND POSSIBILITY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    seqStar2 = SequenceStar()
    selectorStar.add_child(seqStar2)
    # Is there enough material in the incoming edge to begin production ?
    incEdgeChecker = Threshold(incEdge, quantity)
    seqStar2.add_child(incEdgeChecker)
    # If it is the case, repeat production step
    repeater = Repeater()
    seqStar2.add_child(repeater)
    seq = Sequence()
    repeater.add_child(seq)
    # Is there enough space in the node ?
    verifyNode = SpaceChecker(node, nodeStep)
    seq.add_child(verifyNode)
    # If yes, updates it
    consume = Consume(incEdge, node, outEdge, quantity, incStep, nodeStep, minUpdate)
    seq.add_child(consume)
    return seqStar1

def receiptBT(incEdge, node, outEdge):
    """Receipt BT."""
    quantity = NB_WAGONS*WAGON_CAPACITY
    step = quantity/(TRAIN_UNLOADING_TIME/TICK)
    minUpdate = MIN_RECEIPT
    return consumer(incEdge, node, outEdge, quantity, step, step, minUpdate)

def preparationBT(incEdge, node, outEdge):
    """Preparation BT."""
    quantity = MIN_PREPARATION
    step = quantity/(PREPARATION_TIME/TICK)
    minUpdate = MIN_RECEIPT
    return consumer(incEdge, node, outEdge, quantity, step, step, minUpdate)

def shipmentBT(incEdge, node, outEdge):
    """Shipment BT."""
    step = SHIPMENT_SPEED/(60/TICK)
    quantity = BOAT_CAPACITY
    minUpdate = MIN_SHIPMENT
    return consumer(incEdge, node, outEdge, quantity, step, step, minUpdate)

def treatmentBT(incEdge1, incEdge2, node, outEdge):
    """Treatment BT."""
    pitStep = TREATMENT_SPEED/(60/TICK)
    tankStep = MIN_TANK/(60/TICK)
    quantity = MIN_PIT1
    # Minimum to produce before updating the edge (ton)
    minUpdate = 1
    seqStar1 = SequenceStar()
    # Verifies if there is enough space in the pit n°2
    pit2Checker = SpaceChecker(outEdge, quantity)
    seqStar1.add_child(pit2Checker)
    # Selects among one of the two following possibilities
    selectorStar = SelectorStar()
    seqStar1.add_child(selectorStar)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FIRST POSSIBILITY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Is there already material in the node ?
    nodeChecker = ThresholdDec(node, quantity)
    selectorStar.add_child(nodeChecker)
    # Updates the outgoing edge if it the case
    outEdgeUpdater = RawUpdater(node, outEdge, quantity)
    nodeChecker.add_child(outEdgeUpdater)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SECOND POSSIBILITY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    seqStar2 = SequenceStar()
    selectorStar.add_child(seqStar2)
    # Are there enough chemicals in the tank ?
    tankChecker = Threshold(incEdge1, MIN_TANK)
    seqStar2.add_child(tankChecker)
    # Is there enough ore in the pit n°1 ?
    pit1Checker = Threshold(incEdge2, MIN_PIT1)
    seqStar2.add_child(pit1Checker)
    # If it is the case, repeat production step
    repeater = Repeater()
    seqStar2.add_child(repeater)
    seq = Sequence()
    repeater.add_child(seq)
    # Is there enough space in the node ?
    verifyNode = SpaceChecker(node, pitStep)
    seq.add_child(verifyNode)
    # If yes, updates it
    consume = MultipleConsume([incEdge1, incEdge2], node, outEdge, quantity,\
    [tankStep, pitStep], pitStep, minUpdate)
    seq.add_child(consume)
    return seqStar1

# ==================================================================================================

def buildModel(model):
    """Builds the model."""
     # ============ About position and size : ============
    # Size and position values must be between 0 and 100,
    # because they are percentages of the canvas size.
    size = (20, 15)
    # ===================================================
    # ********************** NODES **********************
    trainNode, trainIndex = model.addNode("", "", (0, 0), (0, 20))
    receiptNode, receiptIndex = model.addNode("Réception des produits\nchimiques", MAX_RECEIPT,\
    size, (20, 20))
    miningNode, miningIndex = model.addNode("Extraction du minerai\nbrut de la mine", MAX_MINING,\
    size, (20, 80))
    preparationNode, preparationIndex = \
    model.addNode("Préparation de la mixture\npour le traitement", MAX_PREPARATION, size, (50, 20))
    treatmentNode, treatmentIndex = model.addNode("Traitement du minerai", MAX_TREATMENT,\
    size, (50, 50))
    shipmentNode, shipmentIndex = model.addNode("Expédition", MAX_SHIPMENT, size, (80, 50))
    boatNode, boatIndex = model.addNode("", "", (0, 0), (100, 50))
    # ********************** EDGES **********************
    trainEdge, _ = model.addEdge("Train", MAX_TRAIN, trainIndex, receiptIndex)
    receiptEdge, _ = model.addEdge("", MAX_RECEIPT, receiptIndex, preparationIndex)
    pit1, _ = model.addEdge("pit n°1", MAX_PIT1, miningIndex, treatmentIndex)
    tank, _ = model.addEdge("tank", MAX_TANK, preparationIndex, treatmentIndex)
    pit2, _ = model.addEdge("pit n°2", MAX_PIT2, treatmentIndex, shipmentIndex)
    boatEdge, _ = model.addEdge("Bateau", BOAT_CAPACITY, shipmentIndex, boatIndex)
    # ************************ BT ***********************
    trainNode.bTree = trainBT(trainNode, trainEdge)
    receiptNode.bTree = receiptBT(trainEdge, receiptNode, receiptEdge)
    miningNode.bTree = miningBT(miningNode, pit1)
    preparationNode.bTree = preparationBT(receiptEdge, preparationNode, tank)
    treatmentNode.bTree = treatmentBT(tank, pit1, treatmentNode, pit2)
    shipmentNode.bTree = shipmentBT(pit2, shipmentNode, boatEdge)
    boatNode.bTree = boatBT(boatEdge, boatNode)
