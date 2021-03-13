import pyomo.environ as pyo


class Model:

    def __init__(self, storage_binary):
        self.model = pyo.AbstractModel()
        self.__storage_binary = storage_binary
        self.__setup_model()
        self.__setup_vars()
        self.__setup_parameters()
        self.__setup_constraints()
        self.__setup_objective()

    def __setup_model(self):

        # Number of timestamps
        self.model.n_timestamps = pyo.Param(domain=pyo.PositiveIntegers)

        # Number of PV profiles
        self.model.n_pv = pyo.Param(domain=pyo.NonNegativeIntegers)

        # Number of wind profiles
        self.model.n_wind = pyo.Param(domain=pyo.NonNegativeIntegers)

        # Number of loads of type 1
        self.model.n_load_t1 = pyo.Param(domain=pyo.NonNegativeIntegers)

        # Number of loads of type 2
        self.model.n_load_t2 = pyo.Param(domain=pyo.NonNegativeIntegers)

        # Number of loads of type 3
        self.model.n_load_t3 = pyo.Param(domain=pyo.NonNegativeIntegers)

        # Number of CHP profiles
        self.model.n_chp = pyo.Param(domain=pyo.NonNegativeIntegers)

        # Storage - 1: yes, 0: no
        self.model.storage = pyo.Param(domain=pyo.Binary)

        self.model.T = pyo.RangeSet(0, self.model.n_timestamps - 1)  # 0..95
        self.model.PV = pyo.RangeSet(0, self.model.n_pv - 1)  # 0..n_pv - 1
        self.model.WIND = pyo.RangeSet(0, self.model.n_wind - 1)  # 0..n_pv - 1
        self.model.L1 = pyo.RangeSet(0, self.model.n_load_t1 - 1)  # 0..n_t1_loads - 1
        self.model.L2 = pyo.RangeSet(0, self.model.n_load_t2 - 1)  # 0..n_t2_loads - 1
        self.model.L3 = pyo.RangeSet(0, self.model.n_load_t3 - 1)  # 0..n_t3_loads - 1
        self.model.CHP = pyo.RangeSet(0, self.model.n_chp - 1)  # 0..n_chp - 1

    def __setup_vars(self):

        # Grid energy
        self.model.grid = pyo.Var(self.model.T, domain=pyo.Reals)

        # PV shift
        self.model.pv_shift = pyo.Var(self.model.PV, self.model.T, domain=pyo.Reals)

        # Wind shift
        self.model.wind_shift = pyo.Var(self.model.WIND, self.model.T, domain=pyo.Reals)

        # Type 2 loads shift - Domain contains the constraint x(t) <= 0
        self.model.load_t2_shift = pyo.Var(self.model.L2, self.model.T, domain=pyo.NonPositiveReals)

        # Type 3 loads shift
        self.model.load_t3_shift = pyo.Var(self.model.L3, self.model.T, domain=pyo.Reals)

        # CHP shift
        self.model.chp_shift = pyo.Var(self.model.CHP, self.model.T, domain=pyo.Reals)

        # Storage charge - Domain contains the constraint charge(t) >= 0
        self.model.storage_charge = pyo.Var(self.model.T, domain=pyo.NonNegativeReals)

        # Storage recharge energy (P_in) - Domain contains the constraint in(t) >= 0
        self.model.storage_in = pyo.Var(self.model.T, domain=pyo.NonNegativeReals)

        # Storage discharge energy (P_out) - Domain contains the constraint out(t) >= 0
        self.model.storage_out = pyo.Var(self.model.T, domain=pyo.NonNegativeReals)

    def __setup_parameters(self):

        # PV profiles
        self.model.pv_profiles = pyo.Param(self.model.PV, self.model.T, domain=pyo.Reals)

        # PV profiles min_shift
        self.model.pv_min_shift = pyo.Param(self.model.PV, self.model.T, domain=pyo.Reals)

        # PV profiles max_shift
        self.model.pv_max_shift = pyo.Param(self.model.PV, self.model.T, domain=pyo.Reals)

        # PV profiles total_shift
        self.model.pv_total_shift = pyo.Param(self.model.PV, domain=pyo.Reals)

        # Wind profiles
        self.model.wind_profiles = pyo.Param(self.model.WIND, self.model.T, domain=pyo.Reals)

        # Wind profiles min_shift
        self.model.wind_min_shift = pyo.Param(self.model.WIND, self.model.T, domain=pyo.Reals)

        # Wind profiles max_shift
        self.model.wind_max_shift = pyo.Param(self.model.WIND, self.model.T, domain=pyo.Reals)

        # Wind profiles total_shift
        self.model.wind_total_shift = pyo.Param(self.model.WIND, domain=pyo.Reals)

        # Type 1 load profiles
        self.model.load_t1_profiles = pyo.Param(self.model.L1, self.model.T, domain=pyo.Reals)

        # Type 2 load profiles
        self.model.load_t2_profiles = pyo.Param(self.model.L2, self.model.T, domain=pyo.Reals)

        # Type 2 load allowed Ts for shift
        self.model.load_t2_allowed_t = pyo.Param(self.model.L2, self.model.T, domain=pyo.Binary)

        # Type 2 load allowed reduction on all the time interval
        self.model.load_t2_allowed_reduction_total = pyo.Param(self.model.L2, domain=pyo.PositiveReals)

        # Type 2 load allowed reduction
        self.model.load_t2_allowed_reduction = pyo.Param(self.model.L2, self.model.T, domain=pyo.NonNegativeReals)

        # Type 3 load profiles
        self.model.load_t3_profiles = pyo.Param(self.model.L3, self.model.T, domain=pyo.Reals)

        # Type 3 load allowed Ts for shift
        self.model.load_t3_allowed_t = pyo.Param(self.model.L3, self.model.T, domain=pyo.Binary)

        # Type 3 load min_shift
        self.model.load_t3_min_shift = pyo.Param(self.model.L3, self.model.T, domain=pyo.Reals)

        # Type 3 load max_shift
        self.model.load_t3_max_shift = pyo.Param(self.model.L3, self.model.T, domain=pyo.Reals)

        # Type 3 load total_shift
        self.model.load_t3_total_shift = pyo.Param(self.model.L3, domain=pyo.Reals)

        # CHP profiles
        self.model.chp_profiles = pyo.Param(self.model.CHP, self.model.T, domain=pyo.Reals)

        # CHP allowed Ts for shift
        self.model.chp_allowed_t = pyo.Param(self.model.CHP, self.model.T, domain=pyo.Binary)

        # CHP min_shift
        self.model.chp_min_shift = pyo.Param(self.model.CHP, self.model.T, domain=pyo.Reals)

        # CHP max_shift
        self.model.chp_max_shift = pyo.Param(self.model.CHP, self.model.T, domain=pyo.Reals)

        if self.__storage_binary:
            # Storage initial charge
            self.model.storage_initial_charge = pyo.Param(domain=pyo.NonNegativeReals)

            # Storage max_charge (capacity)
            self.model.storage_max_charge = pyo.Param(domain=pyo.NonNegativeReals)

            # Storage max delta charge
            self.model.storage_max_delta_charge = pyo.Param(self.model.T, domain=pyo.NonNegativeReals)

            # Storage max delta discharge
            self.model.storage_max_delta_discharge = pyo.Param(self.model.T, domain=pyo.NonNegativeReals)

            # Storage charge efficiency
            self.model.storage_charge_efficiency = pyo.Param(domain=pyo.NonNegativeReals)

            # Storage discharge efficiency
            self.model.storage_discharge_efficiency = pyo.Param(domain=pyo.NonNegativeReals)

    def __setup_constraints(self):

        ##############################################################################################
        #
        #   PV
        #
        ##############################################################################################

        # Shift lb
        def pv_shift_lb(m, pv, t):
            return m.pv_shift[pv, t] >= m.pv_min_shift[pv, t]

        self.model.pv_shift_lb = pyo.Constraint(self.model.PV, self.model.T, rule=pv_shift_lb)

        # Shift ub
        def pv_shift_ub(m, pv, t):
            return m.pv_shift[pv, t] <= m.pv_max_shift[pv, t]

        self.model.pv_shift_ub = pyo.Constraint(self.model.PV, self.model.T, rule=pv_shift_ub)

        # Shift at interval t cannot make the profile lower than zero
        def pv_shift_zero(m, pv, t):
            return m.pv_shift[pv, t] <= -m.pv_profiles[pv, t] #TODO -1 rimosso

        self.model.pv_shift_zero = pyo.Constraint(self.model.PV, self.model.T, rule=pv_shift_zero)

        # Shift rule
        def pv_shift_rule(m, pv):
            return sum(m.pv_shift[pv, t] for t in m.T) == m.pv_total_shift[pv]

        self.model.pv_shift_rule = pyo.Constraint(self.model.PV, rule=pv_shift_rule)

        ##############################################################################################
        #
        #   WIND
        #
        ##############################################################################################

        # Shift lb
        def wind_shift_lb(m, w, t):
            return m.wind_shift[w, t] >= m.wind_min_shift[w, t]

        self.model.wind_shift_lb = pyo.Constraint(self.model.WIND, self.model.T, rule=wind_shift_lb)

        # Shift ub
        def wind_shift_ub(m, w, t):
            return m.wind_shift[w, t] <= m.wind_max_shift[w, t]

        self.model.wind_shift_ub = pyo.Constraint(self.model.WIND, self.model.T, rule=wind_shift_ub)

        # Shift at interval t cannot make the profile lower than zero
        def wind_shift_zero(m, w, t):
            return m.wind_shift[w, t] >= m.wind_profiles[w, t]

        self.model.wind_shift_zero = pyo.Constraint(self.model.WIND, self.model.T, rule=wind_shift_zero)

        # Shift rule
        def wind_shift_rule(m, w):
            return sum(m.wind_shift[w, t] for t in m.T) == m.wind_total_shift[w]

        self.model.wind_shift_rule = pyo.Constraint(self.model.WIND, rule=wind_shift_rule)

        ##############################################################################################
        #
        #   Type 2 loads
        #
        ##############################################################################################

        # Shift lb
        def l2_shift_lb(m, l2, t):
            return m.load_t2_shift[l2, t] >= -m.load_t2_allowed_reduction[l2, t] * m.load_t2_allowed_t[l2, t]

        self.model.l2_shift_lb = pyo.Constraint(self.model.L2, self.model.T, rule=l2_shift_lb)

        # Shift at interval t cannot make the profile lower than zero
        def l2_shift_zero(m, l2, t):
            return m.load_t2_shift[l2, t] >= -m.load_t2_profiles[l2, t]

        self.model.l2_shift_zero = pyo.Constraint(self.model.L2, self.model.T, rule=l2_shift_zero)

        # Total allowed shift check
        def l2_total_shift(m, l2):
            return -sum(m.load_t2_shift[l2, t] for t in m.T) <= m.load_t2_allowed_reduction_total[l2]

        self.model.l2_total_shift = pyo.Constraint(self.model.L2, rule=l2_total_shift)

        ##############################################################################################
        #
        #   Type 3 loads
        #
        ##############################################################################################

        # Shift lb
        def l3_shift_lb(m, l3, t):
            return m.load_t3_shift[l3, t] >= m.load_t3_min_shift[l3, t] * m.load_t3_allowed_t[l3, t]

        self.model.l3_shift_lb = pyo.Constraint(self.model.L3, self.model.T, rule=l3_shift_lb)

        # Shift ub
        def l3_shift_ub(m, l3, t):
            return m.load_t3_shift[l3, t] <= m.load_t3_max_shift[l3, t] * m.load_t3_allowed_t[l3, t]

        self.model.l3_shift_ub = pyo.Constraint(self.model.L3, self.model.T, rule=l3_shift_ub)

        # Shift at interval t cannot make the profile lower than zero
        def l3_shift_zero(m, l3, t):
            return m.load_t3_shift[l3, t] >= -m.load_t3_profiles[l3, t]

        self.model.l3_shift_zero = pyo.Constraint(self.model.L3, self.model.T, rule=l3_shift_zero)

        # Shift rule
        def l3_shift_rule_lb(m, l3):
            return sum(m.load_t3_shift[l3, t] for t in m.T) >= -m.load_t3_total_shift[l3]

        self.model.l3_shift_rule_lb = pyo.Constraint(self.model.L3, rule=l3_shift_rule_lb)

        def l3_shift_rule_ub(m, l3):
            return sum(m.load_t3_shift[l3, t] for t in m.T) <= 0

        self.model.l3_shift_rule_ub = pyo.Constraint(self.model.L3, rule=l3_shift_rule_ub)

        ##############################################################################################
        #
        #   CHP
        #
        ##############################################################################################

        # Shift lb
        def chp_shift_lb(m, chp, t):
            return m.chp_shift[chp, t] >= m.chp_min_shift[chp, t] * m.chp_allowed_t[chp, t]

        self.model.chp_shift_lb = pyo.Constraint(self.model.CHP, self.model.T, rule=chp_shift_lb)

        # Shift ub
        def chp_shift_ub(m, chp, t):
            return m.chp_shift[chp, t] <= m.chp_max_shift[chp, t] * m.chp_allowed_t[chp, t]

        self.model.chp_shift_ub = pyo.Constraint(self.model.CHP, self.model.T, rule=chp_shift_ub)

        # Shift at interval t cannot make the profile lower than zero
        def chp_shift_zero(m, chp, t):
            return m.chp_shift[chp, t] <= -m.chp_profiles[chp, t]

        self.model.chp_shift_zero = pyo.Constraint(self.model.CHP, self.model.T, rule=chp_shift_zero)

        # Shift rule
        def chp_shift_rule(m, chp):
            return sum(m.chp_shift[chp, t] for t in m.T) == 0

        self.model.chp_shift_rule = pyo.Constraint(self.model.CHP, rule=chp_shift_rule)

        ##############################################################################################
        #
        #   Storage
        #
        ##############################################################################################

        if self.__storage_binary:
            # Charge ub
            def storage_in_ub(m, t):
                if t == 0:
                    return m.storage_in[t] <= m.storage_max_charge - m.storage_initial_charge
                else:
                    return m.storage_in[t] <= m.storage_max_charge - m.storage_charge[t - 1]

            self.model.storage_in_ub = pyo.Constraint(self.model.T, rule=storage_in_ub)

            # Charge ub 2
            def storage_in_ub_2(m, t):
                return m.storage_in[t] <= m.storage_max_delta_charge[t]

            self.model.storage_in_ub_2 = pyo.Constraint(self.model.T, rule=storage_in_ub_2)

            # Discharge ub
            def storage_out_ub(m, t):
                return m.storage_out[t] <= m.storage_charge[t]

            self.model.storage_out_ub = pyo.Constraint(self.model.T, rule=storage_out_ub)

            # Discharge ub 2
            def storage_out_ub_2(m, t):
                return m.storage_out[t] <= m.storage_max_delta_discharge[t]

            self.model.storage_out_ub_2 = pyo.Constraint(self.model.T, rule=storage_out_ub_2)

            # Charge ub
            def storage_charge_ub(m, t):
                return m.storage_charge[t] <= m.storage_max_charge

            self.model.storage_charge_ub = pyo.Constraint(self.model.T, rule=storage_charge_ub)

            # Charge rule
            def storage_charge_rule(m, t):
                if t == 0:
                    return m.storage_charge[t] == m.storage_initial_charge + m.storage_charge_efficiency * m.storage_in[
                        t] - m.storage_discharge_efficiency * m.storage_out[t]
                else:
                    return m.storage_charge[t] == m.storage_charge[t - 1] + m.storage_charge_efficiency * m.storage_in[
                        t] - m.storage_discharge_efficiency * m.storage_out[t]

            self.model.storage_charge_rule = pyo.Constraint(self.model.T, rule=storage_charge_rule)

        else:

            # No storage rules
            def no_storage_in_bounds(m, t):
                return (0, m.storage_in[t], 0)

            self.model.no_storage_in_bounds = pyo.Constraint(self.model.T, rule=no_storage_in_bounds)

            def no_storage_out_bounds(m, t):
                return (0, m.storage_out[t], 0)

            self.model.no_storage_out_bounds = pyo.Constraint(self.model.T, rule=no_storage_out_bounds)

            def no_storage_charge_bounds(m, t):
                return (0, m.storage_charge[t], 0)

            self.model.no_storage_charge_bounds = pyo.Constraint(self.model.T, rule=no_storage_charge_bounds)

        ##############################################################################################
        #
        #   Power balance
        #
        ##############################################################################################

        def power_balance(m, t):
            return \
                + sum(m.load_t1_profiles[l1, t] for l1 in m.L1) \
                + sum(m.load_t2_profiles[l2, t] + m.load_t2_shift[l2, t] for l2 in m.L2) \
                + sum(m.load_t3_profiles[l3, t] + m.load_t3_shift[l3, t] for l3 in m.L3) \
                + sum(m.pv_profiles[pv, t] - m.pv_shift[pv, t] for pv in m.PV) \
                + sum(m.wind_profiles[w, t] - m.wind_shift[w, t] for w in m.WIND) \
                + sum(m.chp_profiles[chp, t] - m.chp_shift[chp, t] for chp in m.CHP) \
                + (m.storage_in[t] - m.storage_out[t]) \
                - m.grid[t] \
                == 0

        self.model.power_balance = pyo.Constraint(self.model.T, rule=power_balance)

    def __setup_objective(self):

        def objective_function_minimize(m):
            return sum(m.grid[t] for t in m.T)

        self.model.objective_function_minimize = pyo.Objective(sense=pyo.minimize, rule=objective_function_minimize)

        def objective_function_maximize(m):
            return sum(m.grid[t] for t in m.T)

        self.model.objective_function_maximize = pyo.Objective(sense=pyo.maximize, rule=objective_function_maximize)

    def create_instance(self, data):
        return self.model.create_instance(data)
