"""Model builder : nodes, edges, behaviour trees."""

from random import random
from math import sqrt
from bt.base import Sequence, SequenceStar, Threshold, SpaceChecker, Consume, Mine, Train, Boat
from bt.decorator import Delay, Repeater
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

def receiptBT(incEdge, node, outEdge):
    """Receipt BT."""
    # TODO : change quantity
    quantity = NB_WAGONS*WAGON_CAPACITY
    seqStar = SequenceStar()
    # Verifies if material has arrived
    verifyChemicals = Threshold(incEdge, quantity, Threshold.SUPERIOR)
    seqStar.add_child(verifyChemicals)
    # Repeats unloading
    repeater = Repeater()
    seq = Sequence()
    repeater.add_child(seq)
    # Verifies if there is place in the current node
    step = quantity/(TRAIN_UNLOADING_TIME/TICK)
    verifyNode = SpaceChecker(node, step)
    seq.add_child(verifyNode)
    # Decreases incoming value, increases node and outgoing values
    consume = Consume(incEdge, node, outEdge, quantity, step, step, MIN_RECEIPT)
    seq.add_child(consume)
    return seqStar

def miningBT(node, outEdge):
    """Mining BT."""
    nbTicks = MINE_REFRESH_TIME/TICK
    # Minimum to produce before updating the edge (ton)
    minUpdate = 1
    mine = Mine(node, outEdge, triangularDistrib, nbTicks, minUpdate)
    return mine

def preparationBT(incEdge, node, outEdge):
    """Preparation BT."""
    quantity = NB_WAGONS*WAGON_CAPACITY
    seqStar = SequenceStar()
    # Verifies if chemicals are available
    verifyChemicals = Threshold(incEdge, quantity, Threshold.SUPERIOR)
    seqStar.add_child(verifyChemicals)
    # Repeats moving chemicals
    repeater = Repeater()
    seqStar.add_child(repeater)
    seq = Sequence()
    repeater.add_child(seq)
    # Verifies if there is place in the current node
    step = quantity/(TRAIN_UNLOADING_TIME/TICK)
    verifyNode = SpaceChecker(node, step)
    seq.add_child(verifyNode)
    # Decreases incoming value, increases node and outgoing values
    consume = Consume(incEdge, node, outEdge, quantity, step, step, MIN_RECEIPT)
    seq.add_child(consume)
    return seqStar

def treatmentBT(node):
    """Treatment BT."""
    # TODO : complete
    return Threshold(node, 1, Threshold.SUPERIOR)

def shipmentBT(incEdge, node, outEdge):
    """Shipment BT."""
    seqStar = SequenceStar()
    # Verifies if pit n°2 is full enough
    verifyPit = Threshold(incEdge, BOAT_CAPACITY, Threshold.SUPERIOR)
    seqStar.add_child(verifyPit)
    # Repeats loading
    repeater = Repeater()
    seq = Sequence()
    repeater.add_child(seq)
    # Verifies if there is place in the current node
    step = SHIPMENT_SPEED/(60/TICK)
    verifyNode = SpaceChecker(node, step)
    seq.add_child(verifyNode)
    # Decreases incoming value, increases node and outgoing values
    consume = Consume(incEdge, node, outEdge, BOAT_CAPACITY, step, step, MIN_SHIPMENT)
    seq.add_child(consume)
    return seqStar

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
    treatmentNode.bTree = treatmentBT(treatmentNode)
    shipmentNode.bTree = shipmentBT(pit2, shipmentNode, boatEdge)
    boatNode.bTree = boatBT(boatEdge, boatNode)
