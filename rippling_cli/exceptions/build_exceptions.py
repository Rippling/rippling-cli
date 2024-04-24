class PythonCreationFailed(Exception):
    def __init__(self, message="Failed to install Python. Please install Python manually."):
        self.message = message
        super().__init__(self.message)


class DirectoryCreationFailed(Exception):
    def __init__(self, message="Failed to create directory."):
        self.message = message
        super().__init__(self.message)