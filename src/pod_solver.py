import time

import pyomo.environ as pyo
import numpy as np
import copy
from pyomo.opt import SolverStatus, TerminationCondition
from pyomo.core import Var, Objective

from src.chp import CHP
from src.enums import ModelResolveMethod
from src.load import LoadT1, LoadT2, LoadT3
from src.pod_model import Model
from src.pv import PV
from src.wind import Wind
from src.storage import SimpleStorage


class Solver:

    def __init__(self, profiles):
        self.results = None
        self.__profiles = profiles
        self.__model = None

    def __setup_data(self):
        self.pv_array = [p for p in self.__profiles if isinstance(p, PV)]
        self.wind_array = [p for p in self.__profiles if isinstance(p, Wind)]
        self.l1_array = [p for p in self.__profiles if isinstance(p, LoadT1)]
        self.l2_array = [p for p in self.__profiles if isinstance(p, LoadT2)]
        self.l3_array = [p for p in self.__profiles if isinstance(p, LoadT3)]
        self.chp_array = [p for p in self.__profiles if isinstance(p, CHP)]
        self.storage_array = [p for p in self.__profiles if isinstance(p, SimpleStorage)]
        self.data = {
            'n_timestamps': self.__profiles[0].timestamps,
            'n_pv': len(self.pv_array),
            'n_wind': len(self.wind_array),
            'n_load_t1': len(self.l1_array),
            'n_load_t2': len(self.l2_array),
            'n_load_t3': len(self.l3_array),
            'n_chp': len(self.chp_array),
            'storage': len(self.storage_array)
        }
        self.__data_for_instance = self.__init_data()
        self.__setup_result_variable()
        self.__model = Model(self.data['storage'])

        self.__model_parameters_setup()

    def __setup_result_variable(self):
        result_var = {
            'grid': [0 for _ in range(self.data['n_timestamps'])],
            'pv_shift': [[0 for _ in range(self.data['n_timestamps'])] for _ in range(self.data['n_pv'])],
            'wind_shift': [[0 for _ in range(self.data['n_timestamps'])] for _ in range(self.data['n_wind'])],
            'load_t2_shift': [[0 for _ in range(self.data['n_timestamps'])] for _ in range(self.data['n_load_t2'])],
            'load_t3_shift': [[0 for _ in range(self.data['n_timestamps'])] for _ in range(self.data['n_load_t3'])],
            'chp_shift': [[0 for _ in range(self.data['n_timestamps'])] for _ in range(self.data['n_chp'])],
            'storage_charge': [0 for _ in range(self.data['n_timestamps'])],
            'solution_value': None,  # For the solution value
            'time': None,
            'cost': [0 for _ in range(self.data['n_timestamps'])]
        }
        self.results = {
            'minimized': copy.deepcopy(result_var),
            'maximized': copy.deepcopy(result_var),
            'baseline' : [0 for _ in range(self.data['n_timestamps'])]
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
        if self.data['n_pv'] > 0:
            self.add_data_field(field_name='pv_profiles', data=[p.profile for p in self.pv_array])
            self.add_data_field(field_name='pv_min_shift', data=[p.min_shift for p in self.pv_array])
            self.add_data_field(field_name='pv_max_shift', data=[p.max_shift for p in self.pv_array])
            self.add_data_field(field_name='pv_total_shift', data=[p.total_shift for p in self.pv_array])
        if self.data['n_wind'] > 0:
            self.add_data_field(field_name='wind_profiles', data=[p.profile for p in self.wind_array])
            self.add_data_field(field_name='wind_min_shift', data=[p.min_shift for p in self.wind_array])
            self.add_data_field(field_name='wind_max_shift', data=[p.max_shift for p in self.wind_array])
            self.add_data_field(field_name='wind_total_shift', data=[p.total_shift for p in self.wind_array])
        if self.data['n_load_t1'] > 0:
            self.add_data_field(field_name='load_t1_profiles', data=[l.profile for l in self.l1_array])
        if self.data['n_load_t2'] > 0:
            self.add_data_field(field_name='load_t2_profiles', data=[l.profile for l in self.l2_array])
            self.add_data_field(field_name='load_t2_allowed_t', data=[l.allowed_t for l in self.l2_array])
            self.add_data_field(field_name='load_t2_allowed_reduction_total',
                                data=[l.allowed_reduction_total for l in self.l2_array])
            self.add_data_field(field_name='load_t2_allowed_reduction',
                                data=[l.allowed_reduction for l in self.l2_array])
        if self.data['n_load_t3'] > 0:
            self.add_data_field(field_name='load_t3_profiles', data=[l.profile for l in self.l3_array])
            self.add_data_field(field_name='load_t3_allowed_t', data=[l.allowed_t for l in self.l3_array])
            self.add_data_field(field_name='load_t3_min_shift', data=[l.min_shift for l in self.l3_array])
            self.add_data_field(field_name='load_t3_max_shift', data=[l.max_shift for l in self.l3_array])
            self.add_data_field(field_name='load_t3_total_shift', data=[l.total_shift for l in self.l3_array])
        if self.data['n_chp'] > 0:
            self.add_data_field(field_name='chp_profiles', data=[chp.profile for chp in self.chp_array])
            self.add_data_field(field_name='chp_allowed_t', data=[chp.allowed_t for chp in self.chp_array])
            self.add_data_field(field_name='chp_min_shift', data=[chp.min_shift for chp in self.chp_array])
            self.add_data_field(field_name='chp_max_shift', data=[chp.max_shift for chp in self.chp_array])
        if self.data['storage'] > 0:
            st = next(profile for profile in self.__profiles if isinstance(profile, SimpleStorage))
            self.add_data_field(field_name='storage_initial_charge', data=st.initial_charge)
            self.add_data_field(field_name='storage_max_charge', data=st.max_charge)
            self.add_data_field(field_name='storage_max_delta_charge', data=st.max_delta_charge)
            self.add_data_field(field_name='storage_max_delta_discharge', data=st.max_delta_discharge)
            self.add_data_field(field_name='storage_charge_efficiency', data=st.charge_efficiency)
            self.add_data_field(field_name='storage_discharge_efficiency', data=st.discharge_efficiency)

    def get_baseline(self):
        baseline_list = []
        [baseline_list.append(p.profile) for p in self.__profiles]
        baseline_total = [sum(x) for x in zip(*baseline_list)]
        return baseline_total

    def resolve(self, model_resolve_method: ModelResolveMethod, print_results=False, tee=False, pprint=False):

        if len(self.__profiles) == 0:
            raise Exception('Profiles not provided!')
        else:
            self.__setup_data()

        instance = self.__model.create_instance(self.__data_for_instance)
        self.results['baseline'] = self.get_baseline()

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
                if v.name == 'grid':
                    for index in varobject:
                        self.results[model_resolve_method]['grid'][index] = varobject[index].value
                if v.name == 'pv_shift':
                    for index in varobject:
                        self.results[model_resolve_method]['pv_shift'][index[0]][index[1]] = varobject[index].value
                if v.name == 'wind_shift':
                    for index in varobject:
                        self.results[model_resolve_method]['wind_shift'][index[0]][index[1]] = varobject[index].value
                if v.name == 'load_t2_shift':
                    for index in varobject:
                        self.results[model_resolve_method]['load_t2_shift'][index[0]][index[1]] = varobject[index].value
                if v.name == 'load_t3_shift':
                    for index in varobject:
                        self.results[model_resolve_method]['load_t3_shift'][index[0]][index[1]] = varobject[index].value
                if v.name == 'chp_shift':
                    for index in varobject:
                        self.results[model_resolve_method]['chp_shift'][index[0]][index[1]] = varobject[index].value
                if v.name == 'storage_charge':
                    for index in varobject:
                        self.results[model_resolve_method]['storage_charge'][index] = varobject[index].value
            for v in instance.component_objects(Objective, active=True):
                self.results[model_resolve_method]['solution_value'] = v.expr()

            self.results[model_resolve_method]['time'] = end - start

            cost_pv = [[self.pv_array[index].cost_min[t] * (shift[t] < 0) + self.pv_array[index].cost_max[t] * (
                    shift[t] > 0) for t in range(self.data['n_timestamps'])] for index, shift in
                       enumerate(self.results[model_resolve_method]['pv_shift'])] if len(
                self.pv_array) != 0 else [[0] * self.data['n_timestamps']]
            cost_wind = [[self.wind_array[index].cost_min[t] * (shift[t] < 0) + self.wind_array[index].cost_max[t] * (
                    shift[t] > 0) for t in range(self.data['n_timestamps'])] for index, shift in
                         enumerate(self.results[model_resolve_method]['wind_shift'])] if len(
                self.wind_array) != 0 else [[0] * self.data['n_timestamps']]
            # L1 has not costs (shift always zero)
            cost_l2 = [[self.l2_array[index].cost_min[t] * (shift[t] < 0) + self.l2_array[index].cost_max[t] * (
                    shift[t] > 0) for t in range(self.data['n_timestamps'])] for index, shift in
                       enumerate(self.results[model_resolve_method]['load_t2_shift'])] if len(
                self.l2_array) != 0 else [[0] * self.data['n_timestamps']]
            cost_l3 = [[self.l3_array[index].cost_min[t] * (shift[t] < 0) + self.l3_array[index].cost_max[t] * (
                    shift[t] > 0) for t in range(self.data['n_timestamps'])] for index, shift in
                       enumerate(self.results[model_resolve_method]['load_t3_shift'])] if len(
                self.l3_array) != 0 else [[0] * self.data['n_timestamps']]
            cost_chp = [[self.chp_array[index].cost_min[t] * (shift[t] < 0) + self.chp_array[index].cost_max[t] * (
                    shift[t] > 0) for t in range(self.data['n_timestamps'])] for index, shift in
                        enumerate(self.results[model_resolve_method]['chp_shift'])] if len(
                self.chp_array) != 0 else [[0] * self.data['n_timestamps']]

            self.results[model_resolve_method]['cost'] = [
                sum(x) / (len(self.pv_array) + len(self.wind_array) + len(self.l2_array) + len(self.l3_array) + len(
                    self.chp_array)) for x in
                zip([sum(pv_res) for pv_res in zip(*cost_pv)],
                    [sum(wind_res) for wind_res in zip(*cost_wind)],
                    [sum(l2_res) for l2_res in zip(*cost_l2)],
                    [sum(l3_res) for l3_res in zip(*cost_l3)],
                    [sum(chp_res) for chp_res in
                     zip(*cost_chp)])]
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
