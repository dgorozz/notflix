from enum import Enum


class SessionState(str, Enum):
    watching = "watching"
    finished = "finished"