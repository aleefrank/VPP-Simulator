from src.enums import ProfileType
from src.profile import Profile

import numpy as np


# Type 1 loads: not controllable
class LoadT1(Profile):

    def __init__(self, l, timestamps=96, scale_factor=10):
        super().__init__([0 if x < 0 else x * scale_factor for x in l], ProfileType.LOAD_T1, 0, 0, timestamps)

    def get_flexibility(self, type='minimized'):
        if type == 'minimized':
            return [0 for _ in range(self.timestamps)]
        if type == 'maximized':
            return [0 for _ in range(self.timestamps)]


# Type 2 loads: compressible
#   At each timestamp the load can be compressed at most by 'allowed_reduction'
#   The global reduction (sum on the 96 intervals)
class LoadT2(Profile):

    def __init__(self, l, allowed_t: [], allowed_reduction_total=25, allowed_reduction=np.iinfo(np.int32).max,
                 cost_min=0, cost_max=0, timestamps=96, scale_factor=1000):
        super().__init__([0 if x < 0 else x * scale_factor for x in l], ProfileType.LOAD_T2, cost_min, cost_max, timestamps)
        self.allowed_t = [1 if i in allowed_t else 0 for i in range(self.timestamps)]
        self.allowed_reduction_total = sum(l) * allowed_reduction_total / 100
        self.allowed_reduction = self.setup_array_for_property(allowed_reduction)

    def get_flexibility(self, type='minimized'):
        if type == 'minimized':
            return [0 for _ in range(self.timestamps)]
        if type == 'maximized':
            return [0 for _ in range(self.timestamps)]


# Type 3 loads: shiftable
#   At each timestamp the load can be shifted by a value between 'min_shift' and 'max_shift'.
#   Total shifting must be equal to 'total_shifting'
#   Setting total_shifting = 0 will setup the daily conservation
class LoadT3(Profile):

    def __init__(self, l, allowed_t: [], total_shift, min_shift=20, max_shift=20, cost_min=0, cost_max=0,
                 timestamps=96):
        super().__init__([0 if x < 0 else x for x in l], ProfileType.LOAD_T3, cost_min, cost_max, timestamps)
        self.allowed_t = [1 if i in allowed_t else 0 for i in range(self.timestamps)]
        self.min_shift = self.setup_array_for_property([-x * (min_shift / 100) for x in [0 if x < 0 else x for x in l]])
        self.max_shift = self.setup_array_for_property([x * (max_shift / 100) for x in [0 if x < 0 else x for x in l]])

        self.min_flex = self.setup_array_for_property([x - (x * (min_shift / 100)) for x in [0 if x < 0 else x for x in l]])
        self.max_flex = self.setup_array_for_property([x + (x * (max_shift / 100)) for x in [0 if x < 0 else x for x in l]])

        self.total_shift = sum(l) * total_shift / 100

    def get_flexibility(self, type='minimized'):
        if type == 'minimized':
            return [f * a for f, a in zip(self.min_flex, self.allowed_t)]
        if type == 'maximized':
            return [f * a for f, a in zip(self.max_flex, self.allowed_t)]
