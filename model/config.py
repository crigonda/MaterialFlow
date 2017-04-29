"""Parameters of the model."""

# ********************************************* GENERAL ********************************************
TICK = 1 # TIME UNIT (minutes by iteration)
# ============================================== TRAIN =============================================
NB_WAGONS = 12
WAGON_CAPACITY = 30000 # litres
TRAIN_CAPACITY = NB_WAGONS*WAGON_CAPACITY
TRAIN_REFRESH_TIME = 4.3*1440 # 1 day = 1440 minutes
MAX_TRAIN = TRAIN_CAPACITY*2 # litres
# ============================================= RECEIPT ============================================
MAX_RECEIPT = TRAIN_CAPACITY*2 # litres
MAX_RECEIPT_EDGE = TRAIN_CAPACITY*2 # litres
TRAIN_UNLOADING_TIME = 30 # minutes, realistic ?
MIN_RECEIPT = 10000 # litres
# ============================================== MINE ==============================================
MINE_REFRESH_TIME = 1440 # minutes
MAX_MINING = 200 # tons
MAX_PIT1 = 500 # tons
# =========================================== PREPARATION ==========================================
MAX_PREPARATION = TRAIN_CAPACITY*2 # litres
MIN_PREPARATION = MIN_RECEIPT # litres
PREPARATION_TIME = TRAIN_UNLOADING_TIME*(MIN_PREPARATION/TRAIN_CAPACITY) # minutes, realistic ?
MAX_TANK = TRAIN_CAPACITY*2 # litres
# ============================================ TREATMENT ===========================================
MAX_TREATMENT = 200 # tons
MAX_PIT2 = 2500 # tons
MIN_PIT1 = 50 # tons
MIN_TANK = MIN_PIT1*1000 # litres
TREATMENT_SPEED = 10 # tons by hour
# ============================================ SHIPMENT ============================================
MAX_SHIPMENT = 2500 # tons
SHIPMENT_SPEED = 100 # tons by hour
MIN_SHIPMENT = 1 # tons
# ============================================== BOAT ==============================================
BOAT_CAPACITY = 2000 # tons
