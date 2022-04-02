class FileException(Exception):
    """Custom exception to write errors about file
    number or type to console.
    """

    def __init__(self, state, type, inlet):
        self.state = state
        self.inlet = inlet
        self.type = type

    def __str__(self):
        return f"There are {self.state} {self.type} files in the provided folder, please check folder {self.inlet} and refer to docs"
