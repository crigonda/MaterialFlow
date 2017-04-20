"""Model launcher."""

from multiprocessing import Process, Queue
from gui.ModelGUI import ModelGUI
from model.Model import Model
from model.ModelBuilder import buildModel

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
    # Creates the model
    QUEUE = Queue()
    PROC = ModelLauncher(QUEUE)
    # Creates the GUI
    GUI = ModelGUI(PROC)
    # Starts the random walk
    PROC.start()
    # Displays the GUI
    GUI.display()
