from src.enums import ProfileType
from src.profile import Profile


# All parameters are percentage (beside efficiencies)
class SimpleStorage(Profile):

    def __init__(self, max_charge, initial_charge=25, max_delta_charge=60, max_delta_discharge=60,
                 charge_efficiency=0.95, discharge_efficiency=0.95, timestamps=96):
        super().__init__([0] * timestamps, ProfileType.STORAGE, 0, 0, timestamps)
        self.initial_charge = max_charge * initial_charge / 100
        self.max_charge = max_charge
        self.max_delta_charge = self.setup_array_for_property(max_charge * max_delta_charge / 100)
        self.max_delta_discharge = self.setup_array_for_property(max_charge * max_delta_discharge / 100)
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency

    def get_flexibility(self, type='minimized'):
        if type == 'minimized':
            return self.max_delta_discharge
        if type == 'maximized':
            return self.max_delta_charge
