"""Parameters of the model."""

# ********************************************* GENERAL ********************************************
TICK = 1 # TIME UNIT (in min)
# ============================================== TRAIN =============================================
NB_TRAINS = 1 # Trains a day
NB_WAGONS = 12
WAGON_CAPACITY = 30000
TRAIN_CAPACITY = NB_WAGONS*WAGON_CAPACITY
TRAIN_REFRESH_TIME = 500 #1440
MAX_TRAIN = TRAIN_CAPACITY*3
# ============================================= RECEIPT ============================================
MAX_RECEIPT = TRAIN_CAPACITY*2
MAX_RECEIPT_EDGE = TRAIN_CAPACITY*3
TRAIN_UNLOADING_TIME = 30 # TODO : realistic ?
MIN_RECEIPT = 10000
# ============================================== MINE ==============================================
MINE_REFRESH_TIME = 1440
MAX_MINING = 100
MAX_PIT1 = 200
# =========================================== PREPARATION ==========================================
MAX_PREPARATION = TRAIN_CAPACITY*2
PREPARATION_TIME = TRAIN_UNLOADING_TIME/(MAX_TRAIN/MIN_RECEIPT) # TODO : realistic ?
MIN_PREPARATION = MIN_RECEIPT
MAX_TANK = TRAIN_CAPACITY*3
# ============================================ TREATMENT ===========================================
MAX_TREATMENT = 100
MAX_PIT2 = 3000
MIN_PIT1 = 50
MIN_TANK = MIN_PIT1*1000
TREATMENT_SPEED = 10 # tons by hour
# ============================================ SHIPMENT ============================================
MAX_SHIPMENT = 3000
SHIPMENT_SPEED = 100 # tons by hour
MIN_SHIPMENT = 1
# ============================================== BOAT ==============================================
BOAT_CAPACITY = 2000

