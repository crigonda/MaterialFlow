"""Parameters of the model."""

# ********************************************* GENERAL ********************************************
TICK = 1 # TIME UNIT (in min)
# ============================================== TRAIN =============================================
NB_TRAINS = 1
NB_WAGONS = 12
WAGON_CAPACITY = 30000
TRAIN_REFRESH_TIME = 1440
MAX_TRAIN = NB_WAGONS*WAGON_CAPACITY*2
# ============================================= RECEIPT ============================================
MAX_RECEIPT = 500000
TRAIN_UNLOADING_TIME = 30 # TODO : realistic ?
MIN_RECEIPT = 10000
# ============================================== MINE ==============================================
MINE_REFRESH_TIME = 1440
MAX_MINING = 1000
MAX_PIT1 = 100
# =========================================== PREPARATION ==========================================
MAX_PREPARATION = MAX_RECEIPT
PREPARATION_TIME = 30 # TODO : realistic ?
MIN_PREPARATION = MIN_RECEIPT
MAX_TANK = 500000
# ============================================ TREATMENT ===========================================
MAX_TREATMENT = 10000
MAX_PIT2 = 2000
# ============================================ SHIPMENT ============================================
MAX_SHIPMENT = 10000
SHIPMENT_SPEED = 100 # tons by hour
MIN_SHIPMENT = 10
# ============================================== BOAT ==============================================
BOAT_CAPACITY = 2000

