"""Model launcher."""

from multiprocessing import Process, Queue
from gui.ModelGUI import ModelGUI
from model.Model import Model
from model.ModelBuilder import buildModel
from model.config import TICK

class ModelLauncher(Process):
    """Model launcher."""

    def __init__(self, guiQueue=None):
        super(ModelLauncher, self).__init__()
        self.queue = guiQueue
        # Creates and builds the model
        self.model = Model(guiQueue)
        buildModel(self.model)

    def run(self):
        """Runs the simulation."""
        while True:
            self.model.run()

    def getQueue(self):
        """Returns the queue."""
        return self.queue

# ========================================== LAUNCHER PART =========================================
if __name__ == '__main__':
    # Size of the GUI queue : increase if more memory available
    # To synchronize the GUI and the model, simply set to 1
    QUEUE_SIZE = 100
    # Creates the model
    QUEUE = Queue(QUEUE_SIZE)
    PROC = ModelLauncher(QUEUE)
    # Creates the GUI
    GUI = ModelGUI(PROC, TICK)
    # Starts the random walk
    PROC.start()
    # Displays the GUI
    GUI.display()
