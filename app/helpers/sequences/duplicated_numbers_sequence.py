from .sequence_strategy import SequenceStrategy

class DuplicatedNumbersSequence(SequenceStrategy):
    def __init__(self):
        """
        Initializes a DuplicatedNumbersSequence object.

        This sets the initial value of the sequence to 1.
        """
        self.initialize()

    def initialize(self):
        """
        Sets the sequence to its initial state.

        The initial value of the sequence is set to 1.
        """
        self.current_value = 0.5
        
    def reset(self):
        """
        Resets the sequence to its initial state.

        This method is equivalent to calling initialize().
        """
        self.initialize()

    def current(self):
        """
        Gets the current value of the sequence.

        Returns:
            int: The current value of the sequence.
        """
        return self.current_value

    def next(self):
        """
        Advances the sequence by doubling the current value.

        If the current value is 1, it returns 2 without doubling.

        Returns:
            int: The next value in the sequence.
        """
        self.current_value *= 2
        return self.current_value


    def previous(self):
        self.current_value /= 2
        return self.current_value

    def generate_sequence(self, length):
        """
        Generates a sequence of duplicated numbers up to the specified length.

        Args:
            length (int): The length of the sequence to generate.

        Returns:
            list: A list containing the generated sequence.
        """
        return [2**i for i in range(length)]
