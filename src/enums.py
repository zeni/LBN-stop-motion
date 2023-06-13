from enum import Enum


class PathType(Enum):
    LINEAR = 0
    RATIO = 1
    HALF = 2


class PathMotion(Enum):
    CONST = 0
    ACC = 1
    DEC = 2
    PARA = 3


class Mode(Enum):
    PATH = 0
    ANNO = 1
