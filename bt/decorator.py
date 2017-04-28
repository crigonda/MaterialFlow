"""Decorators."""
from bt.base import Task, Decorator

class Delay(Decorator):
    """ Decorator base sur un simple delay. Il y a un seul child. """

    def __init__(self, delay=0):
        super().__init__()
        self.delay = delay
        self._delay = delay

    def run(self):
        #print("compteur: ", self.delay)
        if self.delay > 0:
            self.delay -= 1
            return Task.RUNNING
        else:
            status = self._children[0].run()
            if status == Task.SUCCES:
                self.delay = self._delay
                return Task.SUCCES
            elif status == Task.RUNNING:
                return Task.RUNNING
            else:
                self.delay = self._delay
                return Task.ECHEC

    def add_child(self, c):
        super().add_child(c)

class Repeater(Decorator):
    """ Retourne l'etat RUNNING tant que son enfant n'a pas retourne SUCCES"""

    def __init__(self):
        super().__init__()

    def run(self):
        status = self._children[0].run()
        if status == Task.SUCCES:
            return Task.SUCCES
        else:
            return Task.RUNNING

    def add_child(self, c):
        super().add_child(c)

# ==================================================================================================

class ThresholdDec(Decorator):
    """Threshold condition decorator."""
    # Comparison type
    INFERIOR, SUPERIOR = range(2)

    def __init__(self, element, threshold, comp=SUPERIOR):
        super().__init__()
        self.element = element
        self.threshold = threshold
        if comp == ThresholdDec.INFERIOR:
            self.cond = self._inf
        else:
            self.cond = self._sup

    def _inf(self):
        """Inferior."""
        if self.element.current <= self.threshold:
            return True
        else:
            return False

    def _sup(self):
        """Superior."""
        if self.element.current >= self.threshold:
            return True
        else:
            return False

    def run(self):
        if self.cond():
            status = self._children[0].run()
            return status
        else:
            return Task.ECHEC

    def add_child(self, c):
        super().add_child(c)
