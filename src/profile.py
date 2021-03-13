import numpy as np
from src.enums import ProfileType


class Profile(object):

    def __init__(self, l, profile_type=ProfileType.NA, cost_min=0, cost_max=0, timestamps=96):
        self.profile_type = profile_type
        self.timestamps = timestamps
        self.profile = self.__setup_profile_array(l)
        self.cost_min = self.setup_array_for_property(cost_min)
        self.cost_max = self.setup_array_for_property(cost_max)

    def append(self, value):
        self.profile.append(value)

    def __getitem__(self, item):
        return self.profile[item]

    def __setitem__(self, key, value):
        self.profile[key] = value

    def __repr__(self):
        return self.profile

    def __str__(self):
        return self.profile.__str__()

    def __setup_profile_array(self, l):
        if self.timestamps % len(l) != 0:
            raise Exception('The number of timestamps must be multiple of the length of passed parameters.')
        if self.profile_type == ProfileType.NA or self.profile_type == ProfileType.ZERO:
            result = [0] * self.timestamps
        else:
            result = np.repeat(l, self.timestamps / len(l))
        return result

    def setup_array_for_property(self, value):
        if isinstance(value, (list, np.ndarray)):
            if self.timestamps != len(value):
                raise Exception('{} length is not equal to the number of timestamps.'.format(value))
            return value
        else:
            return [value] * self.timestamps
