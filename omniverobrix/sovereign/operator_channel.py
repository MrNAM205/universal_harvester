class OperatorChannel:
    def __init__(self):
        self.halt_flag = False
        self.pause_flag = False
        self.overrides = []

    def snapshot(self) -> dict:
        return {
            "halt": self.halt_flag,
            "pause": self.pause_flag,
            "overrides": list(self.overrides),
        }

    def has_hard_halt(self) -> bool:
        return self.halt_flag

    def has_pause(self) -> bool:
        return self.pause_flag
