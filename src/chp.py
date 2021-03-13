from src.enums import ProfileType
from src.profile import Profile


class CHP(Profile):

    def __init__(self, l, allowed_t: [], scale_factor=10, min_shift=10, max_shift=10, cost_min=0, cost_max=0,
                 timestamps=96):
        super().__init__([x * scale_factor if x < 0 else x for x in l], ProfileType.CHP, cost_min, cost_max, timestamps)

        self.scale_factor = scale_factor
        self.allowed_t = [1 if i in allowed_t else 0 for i in range(self.timestamps)]
        self.min_shift = self.setup_array_for_property([x * (min_shift / 100) * self.scale_factor for x in l])
        self.max_shift = self.setup_array_for_property([-x * (max_shift / 100) * self.scale_factor for x in l])

        self.min_flex = self.setup_array_for_property(
            [(x * self.scale_factor - (x * self.scale_factor * (min_shift / 100))) for x in l])
        self.max_flex = self.setup_array_for_property(
            [(x * self.scale_factor + (x * self.scale_factor * (max_shift / 100))) for x in l])

    def get_flexibility(self, type='minimized'):
        if type == 'minimized':
            return [s * a for s, a in zip(self.max_flex, self.allowed_t)]
        if type == 'maximized':
            return [s * a for s, a in zip(self.min_flex, self.allowed_t)]
