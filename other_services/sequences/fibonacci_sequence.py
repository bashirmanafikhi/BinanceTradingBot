from .sequence_strategy import SequenceStrategy

class FibonacciSequence(SequenceStrategy):
    def __init__(self):
        self.initialize()
    
    def reset(self):
        """
        Reset the Fibonacci sequence to its initial state.

        This method sets the sequence back to the starting values.
        """
        self.initialize()

    def current(self):
        """
        Get the current value of the Fibonacci sequence.

        Returns:
            int: The current value of the Fibonacci sequence.
        """
        return self.curr
    
    def initialize(self):
        self.prev = 1
        self.curr = 1

    def next(self):
        result = self.curr
        self.prev, self.curr = self.curr, self.prev + self.curr
        return result

    def generate_sequence(self, length):
        sequence = [1, 2]  # Initial values
        while len(sequence) < length:
            sequence.append(self.next())
        return sequence[:length]
