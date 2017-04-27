"""GUI for model rendering."""

from tkinter import Tk, PanedWindow, Canvas, LabelFrame, Scale, DoubleVar
from tkinter import TOP, Y, BOTH, ALL, VERTICAL, HORIZONTAL
from time import sleep
import queue

# Default parameters
DEFAULT_REFRESH_RATE = 1
CANVAS_X = 1000
CANVAS_Y = 700
BG_COLOR = '#f0f8ff'

class ModelGUI(object):
    """Rendering of the model."""
    def __init__(self, modelProc):
        self.modelProc = modelProc
        self.queue = modelProc.getQueue()
        # ----------------- Model parameters -----------------
        # Waiting time between two events
        self.refreshRate = DEFAULT_REFRESH_RATE
        # Current simulation step
        self.count = 0
        # ------------------------ GUI -----------------------
        # Main window
        self.window = Tk()
        self.window.title("Model Rendering")
        self.window.configure(bg=BG_COLOR)
        self.window.protocol("WM_DELETE_WINDOW", self.onClosing)
        # Main pane
        mainPane = PanedWindow(self.window, orient=HORIZONTAL, bg=BG_COLOR)
        mainPane.pack(side=TOP, expand=Y, fill=BOTH, pady=5, padx=5)
        # Canvas frame
        canvasFrame = LabelFrame(mainPane, text="Rendering", padx=10, pady=10, bg=BG_COLOR)
        mainPane.add(canvasFrame)
        self.canvas = Canvas(canvasFrame, width=CANVAS_X, height=CANVAS_Y, background="white")
        self.canvas.pack()
        # Parameters frame
        paramFrame = LabelFrame(mainPane, text="Simulation parameters",\
        padx=20, pady=20, bg=BG_COLOR)
        mainPane.add(paramFrame)
        # ===> Refresh rate slider
        self.stepVar = DoubleVar(paramFrame, value=DEFAULT_REFRESH_RATE)
        slider = Scale(paramFrame, from_=0, to_=1, resolution=0.01, length=350, orient=VERTICAL,\
        variable=self.stepVar, label="# Refresh rate", bg=BG_COLOR, bd=1)
        slider.bind("<ButtonRelease-1>", self.updateRate)
        slider.grid(row=1, column=1)
        # Rows and columns configuration
        paramFrame.grid_columnconfigure(0, weight=1)
        paramFrame.grid_columnconfigure(1, weight=2)
        paramFrame.grid_columnconfigure(2, weight=1)
        paramFrame.grid_rowconfigure(0, weight=1)
        paramFrame.grid_rowconfigure(2, weight=2)

    def onClosing(self):
        """Called when exiting the window."""
        self.modelProc.terminate()
        self.window.destroy()

    def display(self):
        """Display the GUI."""
        # Sleep some time to be sure queue is not empty
        sleep(0.5)
        self.window.after(int(self.refreshRate*1000), self.update)
        self.window.mainloop()

    def update(self):
        """Tries to get a new version of the labels list."""
        try:
            model = self.queue.get(False)
            self.updateRendering(model)
            self.window.after(int(self.refreshRate*1000), self.update)
        except queue.Empty:
            print("Queue is empty !!")
            self.window.after(int(self.refreshRate*1000), self.update)

    def updateRendering(self, model):
        """Updates the rendering."""
        self.cleanCanvas()
        nodes, edges = model
        # Draws the nodes
        for node in nodes:
            node.draw(self.canvas, CANVAS_X, CANVAS_Y)
        # Draws the edges
        for edge in edges:
            edge.draw(self.canvas, CANVAS_X, CANVAS_Y)

    def updateRate(self, event):
        """Updates the refresh rate when the slider is moved."""
        self.refreshRate = self.stepVar.get()

    def cleanCanvas(self):
        """Cleans the canvas."""
        self.canvas.delete(ALL)
