from enum import Enum


class ProfileType(Enum):
    LOAD_T1 = 'LOAD_T1'
    LOAD_T2 = 'LOAD_T2'
    LOAD_T3 = 'LOAD_T3'
    PV = 'PV'
    WIND = 'WIND'
    CHP = 'CHP'
    PONTLAB = 'PONTLAB'
    BESS = 'BESS'
    STORAGE = 'STORAGE'
    PRICE = 'PRICE'
    ZERO = 'ZERO'
    NA = 'NA'  # Not available, not specified


class ModelResolveMethod(Enum):
    MINIMIZE = 1
    MAXIMIZE = 2
    MINIMIZE_AND_MAXIMIZE = 3
