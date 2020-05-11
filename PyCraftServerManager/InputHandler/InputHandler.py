from ..Utilities.Singleton import Singleton

@Singleton
class InputHandler():
    """
    Input Handler handles accepting user input, or scheduled commands.

    Used Singleton decorator to ensure only one exists.
    """
    
    def __init__(self):
        """
        Initializes Input Handler.
        """
        super().__init__()

    