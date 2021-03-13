import pyomo.environ as pyo


class Model:

    def __init__(self):
        self.model = pyo.AbstractModel()
        self.__setup_model()
        self.__setup_vars()
        self.__setup_parameters()
        self.__setup_constraints()
        self.__setup_objective()

    def __setup_model(self):
        # Number of timestamps
        self.model.n_timestamps = pyo.Param(domain=pyo.PositiveIntegers)
        # Number of Pods
        self.model.n_pods = pyo.Param(domain=pyo.PositiveIntegers)

        self.model.T = pyo.RangeSet(0, self.model.n_timestamps - 1)  # 0..95
        self.model.N = pyo.RangeSet(0, self.model.n_pods - 1)  # 0..n - 1

    def __setup_vars(self):
        # Max flexibility
        self.model.F_max = pyo.Var(self.model.T, domain=pyo.Reals)

        # Min flexibility
        self.model.F_min = pyo.Var(self.model.T, domain=pyo.Reals)

        # Gain
        self.model.G_in = pyo.Var(self.model.T, domain=pyo.Reals)
        self.model.G_out = pyo.Var(self.model.T, domain=pyo.Reals)
        self.model.Gain_max = pyo.Var(self.model.T, domain=pyo.Reals)
        self.model.Gain_min = pyo.Var(self.model.T, domain=pyo.Reals)

    def __setup_parameters(self):
        # Sum of Pod baselines
        self.model.baseline = pyo.Param(self.model.T, domain=pyo.Reals)
        # Max Pod flexibilities
        self.model.pod_max_flex = pyo.Param(self.model.N, self.model.T, domain=pyo.Reals)
        # Min Pod flexibilities
        self.model.pod_min_flex = pyo.Param(self.model.N, self.model.T, domain=pyo.Reals)

        # Costs
        self.model.c_in = pyo.Param(self.model.T, domain=pyo.Reals)
        self.model.c_out = pyo.Param(self.model.T, domain=pyo.Reals)
        self.model.c_p = pyo.Param(self.model.T, domain=pyo.Reals)

        # Cases
        self.model.max_can_buy = pyo.Param(self.model.T, default=0, domain=pyo.Binary, mutable=True)
        self.model.max_can_sell = pyo.Param(self.model.T, default=0, domain=pyo.Binary, mutable=True)
        self.model.min_can_buy = pyo.Param(self.model.T, default=0, domain=pyo.Binary, mutable=True)
        self.model.min_can_sell = pyo.Param(self.model.T, default=0, domain=pyo.Binary, mutable=True)

    def __setup_constraints(self):
        ##############################################################################################
        #
        #   F_max
        #
        ##############################################################################################
        # F_max lb
        def F_max_lb(m, t):
            return m.F_max[t] >= m.baseline[t]

        self.model.F_max_lb = pyo.Constraint(self.model.T, rule=F_max_lb)

        # F_max ub
        def F_max_ub(m, t):
            return m.F_max[t] <= sum(m.pod_max_flex[n, t] for n in m.N)

        self.model.F_max_ub = pyo.Constraint(self.model.T, rule=F_max_ub)

        ##############################################################################################
        #
        #   F_min
        #
        ##############################################################################################
        # F_min lb
        def F_min_lb(m, t):
            return m.F_min[t] >= sum(m.pod_min_flex[n, t] for n in m.N)

        self.model.F_min_lb = pyo.Constraint(self.model.T, rule=F_min_lb)

        # F_min ub
        def F_min_ub(m, t):
            return m.F_min[t] <= m.baseline[t]

        self.model.F_min_ub = pyo.Constraint(self.model.T, rule=F_min_ub)


        ##############################################################################################
        #
        #   G_in / G_out value
        #
        ##############################################################################################
        # Gain_in
        def G_in_value(m, t):
            return m.G_in[t] == m.c_p[t] - m.c_in[t]

        self.model.G_in_value = pyo.Constraint(self.model.T, rule=G_in_value)

        # Gain_out
        def G_out_value(m, t):
            return m.G_out[t] == m.c_out[t] - m.c_p[t]

        self.model.G_out_value = pyo.Constraint(self.model.T, rule=G_out_value)

        ##############################################################################################
        #
        #   GAIN
        #
        ##############################################################################################
        def gain_max_rule(m, t):
            return m.Gain_max[t] == (m.G_in[t] * m.max_can_buy[t] - m.G_out[t] * m.max_can_sell[t])

        self.model.gain_max_rule = pyo.Constraint(self.model.T, rule=gain_max_rule)

        def gain_min_rule(m, t):
            return m.Gain_min[t] == (m.G_in[t] * m.min_can_buy[t] - m.G_out[t] * m.min_can_sell[t])

        self.model.gain_min_rule = pyo.Constraint(self.model.T, rule=gain_min_rule)

    def __setup_objective(self):
        def objective_function_minimize(m):
            return sum(m.Gain_max[t] * m.F_max[t] + m.Gain_min[t] * m.F_min[t] for t in m.T)

        self.model.objective_function_minimize = pyo.Objective(sense=pyo.minimize, rule=objective_function_minimize)

        def objective_function_maximize(m):
            return sum(m.Gain_max[t] * m.F_max[t] + m.Gain_min[t] * m.F_min[t] for t in m.T)

        self.model.objective_function_maximize = pyo.Objective(sense=pyo.maximize, rule=objective_function_maximize)

    def create_instance(self, data):
        return self.model.create_instance(data)
