from abc import ABC

# Define a strategy interface
class SequenceStrategy:
    """
    Base class for sequence generators.

    This class defines the interface for sequence generators.
    """

    def next(self):
        """
        Advance the sequence to the next element.

        Returns:
            Any: The next element in the sequence.
        """
        raise NotImplementedError("Subclasses must implement the 'next' method.")

    def generate_sequence(self, length):
        """
        Generate a sequence up to the specified length.

        Args:
            length (int): The length of the sequence to generate.

        Returns:
            list: A list containing the generated sequence.
        """
        raise NotImplementedError("Subclasses must implement the 'generate_sequence' method.")

    def reset(self):
        """
        Reset the sequence to its initial state.

        """
        pass

    def current(self):
        """
        Get the current value of the sequence.

        Returns:
            Any: The current value of the sequence.
        """
        pass
