import time

import pyomo.environ as pyo
import numpy as np
import copy
from pyomo.opt import SolverStatus, TerminationCondition
from pyomo.core import Var, Objective

from src.enums import ModelResolveMethod
from src.aggregator_model import Model


class Solver:

    def __init__(self, input_data):
        self.results = None
        self.__input_data = input_data
        self.__model = None

    def __setup_data(self):

        self.baseline = self.__input_data['baseline']
        self.max_flex_array = self.__input_data['maximized']['flexibilities']
        self.min_flex_array = self.__input_data['minimized']['flexibilities']
        self.c_in = self.__input_data['costs']['buy']
        self.c_out = self.__input_data['costs']['sell']
        self.c_p = self.__input_data['costs']['production']

        self.data = {
            'n_timestamps': 96,  # TODO
            'n_pods': len(self.min_flex_array)  # len(self.__input_data[0][0]
        }
        self.__data_for_instance = self.__init_data()
        self.__setup_result_variable()
        self.__model = Model()

        self.__model_parameters_setup()

    def __setup_result_variable(self):
        result_var = {
            'Old_f_max': [sum(col) for col in zip(*self.__input_data['maximized']['flexibilities'])],
            'Old_f_min': [sum(col) for col in zip(*self.__input_data['minimized']['flexibilities'])],
            'baseline': self.baseline,

            'F_max': [0 for _ in range(self.data['n_timestamps'])],
            'F_min': [0 for _ in range(self.data['n_timestamps'])],
            'Gain_max': [0 for _ in range(self.data['n_timestamps'])],
            'Gain_min': [0 for _ in range(self.data['n_timestamps'])],

            'solution_value': None,  # For the solution value
            'time': None,
        }
        # print(result_var['F_max'])
        self.results = {
            'maximized': copy.deepcopy(result_var)
        }

    def __init_data(self):
        result = {None: {}}
        for key, value in self.data.items():
            result[None][key] = {None: value}

        return result

    def add_data_field(self, field_name, data):
        if isinstance(data, list):
            if len(data) < 1:
                raise Exception('{} data with no length'.format(field_name))
            else:
                if isinstance(data[0], (list, np.ndarray)):
                    self.add_multidimension_array_data_field(field_name, data, len(data[0]))
                else:
                    self.add_array_data_field(field_name, data)
        else:
            self.add_single_field(field_name, data)

    def add_single_field(self, field_name, value):
        self.__data_for_instance[None][field_name] = {None: value}

    def add_array_data_field(self, field_name, data):
        self.__data_for_instance[None][field_name] = {}
        for i in range(len(data)):
            self.__data_for_instance[None][field_name][i] = data[i]

    def add_multidimension_array_data_field(self, field_name, data, nested_dimension):
        self.__data_for_instance[None][field_name] = {}
        for i in range(len(data)):
            for j in range(nested_dimension):
                self.__data_for_instance[None][field_name][(i, j)] = data[i][j]

    def __model_parameters_setup(self):
        def __init_max_can_buy(a):
            sum_max = [sum(col) for col in zip(*a)]
            return [1 if i > 0 else 0 for i in sum_max]

        def __init_max_can_sell(a, b):
            sum_max = [sum(col) for col in zip(*a)]
            return [1 if (x <= 0 or y <= 0) else 0 for x, y in zip(sum_max, b)]

        def __init_min_can_buy(a, b):
            sum_min = [sum(col) for col in zip(*a)]
            return [1 if (x >= 0 or y >= 0) else 0 for x, y in zip(sum_min, b)]

        def __init_min_can_sell(a):
            sum_min = [sum(col) for col in zip(*a)]
            return [1 if x < 0 else 0 for x in sum_min]

        self.add_data_field(field_name='baseline', data=[p for p in self.baseline])
        self.add_data_field(field_name='pod_max_flex', data=[p for p in self.max_flex_array])
        self.add_data_field(field_name='pod_min_flex', data=[p for p in self.min_flex_array])

        self.add_data_field(field_name='max_can_buy', data=__init_max_can_buy(self.max_flex_array))
        self.add_data_field(field_name='max_can_sell', data=__init_max_can_sell(self.max_flex_array, self.baseline))
        self.add_data_field(field_name='min_can_buy', data=__init_min_can_buy(self.min_flex_array, self.baseline))
        self.add_data_field(field_name='min_can_sell', data=__init_min_can_sell(self.min_flex_array))
        self.add_data_field(field_name='c_in', data=self.c_in)
        self.add_data_field(field_name='c_out', data=self.c_out)
        self.add_data_field(field_name='c_p', data=self.c_p)

    def resolve(self, model_resolve_method: ModelResolveMethod, print_results=True, tee=True, pprint=True):

        if len(self.__input_data) == 0:
            raise Exception('input_data not provided!')
        else:
            self.__setup_data()

        instance = self.__model.create_instance(self.__data_for_instance)

        if pprint:
            instance.pprint()

        if model_resolve_method == ModelResolveMethod.MINIMIZE:
            instance.objective_function_minimize.activate()
            instance.objective_function_maximize.deactivate()
            self.__resolve_model_and_results('minimized', instance, tee, pprint)
            if print_results:
                print('Optimal solution - minimized: %5.2f' % self.results['minimized']['solution_value'])
                print('Time - minimized: {}'.format(self.results['minimized']['time']))

        elif model_resolve_method == ModelResolveMethod.MAXIMIZE:

            instance.objective_function_minimize.deactivate()
            instance.objective_function_maximize.activate()
            self.__resolve_model_and_results('maximized', instance, tee, pprint)
            if print_results:
                print('Optimal solution - maximized: %5.2f' % self.results['maximized']['solution_value'])
                print('Time - maximized: {}'.format(self.results['maximized']['time']))

        elif model_resolve_method == ModelResolveMethod.MINIMIZE_AND_MAXIMIZE:

            instance.objective_function_minimize.activate()
            instance.objective_function_maximize.deactivate()
            self.__resolve_model_and_results('minimized', instance, tee, pprint)
            instance.objective_function_minimize.deactivate()
            instance.objective_function_maximize.activate()
            self.__resolve_model_and_results('maximized', instance, tee, pprint)
            if print_results:
                print('Optimal solution - minimized: %5.2f' % self.results['minimized']['solution_value'])
                print('Optimal solution - maximized: %5.2f' % self.results['maximized']['solution_value'])
                print('Time - minimized: {}'.format(self.results['minimized']['time']))
                print('Time - maximized: {}'.format(self.results['maximized']['time']))

    def __resolve_model_and_results(self, model_resolve_method, instance, tee, pprint):

        start = time.time()

        solver = pyo.SolverFactory('gurobi', solver_io="python")

        solver.options['NonConvex'] = 2
        result = solver.solve(instance, tee=tee)

        end = time.time()

        if pprint:
            instance.pprint()

        # Check the results and extract the values if the solution is optimal
        if (result.solver.status == SolverStatus.ok) and (
                result.solver.termination_condition == TerminationCondition.optimal):

            # instance.pprint()

            for v in instance.component_objects(Var, active=True):
                # print ("Variable",v)
                varobject = getattr(instance, str(v))
                if v.name == 'F_max':
                    for index in varobject:
                        self.results[model_resolve_method]['F_max'][index] = varobject[index].value
                if v.name == 'F_min':
                    for index in varobject:
                        self.results[model_resolve_method]['F_min'][index] = varobject[index].value
                if v.name == 'Gain_max':
                    for index in varobject:
                        self.results[model_resolve_method]['Gain_max'][index] = varobject[index].value
                if v.name == 'Gain_min':
                    for index in varobject:
                        self.results[model_resolve_method]['Gain_min'][index] = varobject[index].value

            for v in instance.component_objects(Objective, active=True):
                self.results[model_resolve_method]['solution_value'] = v.expr()

            self.results[model_resolve_method]['time'] = end - start

            # cost = [[0] * self.data['n_timestamps']]

            # self.results[model_resolve_method]['cost'] = [[sum(res) for res in zip(*cost)]]
            # print(self.results[model_resolve_method]['cost'])

        elif result.solver.termination_condition == TerminationCondition.infeasible:
            print('############################ INFEASIBLE MODEL ############################')
            raise Exception('############################ INFEASIBLE MODEL ############################')
        else:
            print('############################ SOMETHING WENT WRONG ############################')
            print("Solver Status: ", result.solver.status)
            raise Exception(
                "############################ SOMETHING WENT WRONG ############################\nSolver Status: ",
                result.solver.status)
