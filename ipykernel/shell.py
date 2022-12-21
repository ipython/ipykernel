from .athread import AThread


class ShellThread(AThread):
    def __init__(self, name: str):
        super().__init__(name=f"Shell:{name}")
