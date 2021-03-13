from src.enums import ModelResolveMethod
from src.load import LoadT3, LoadT2
from src.profile import Profile
from src.pv import PV
from src.wind import Wind
from src.pod_solver import Solver
from src.storage import SimpleStorage
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set()


class Pod(object):

    def __init__(self, init_list=None, profiles=None, name=None):
        self.name = name
        self.profiles = []
        self.solver = None
        self.resolve_method = None
        self.to_optimize = False

        if init_list is not None:
            if isinstance(init_list, list):
                self.set_profiles(init_list)
            else:
                self.set_profiles([init_list])

    def set_name(self, name):
        self.name = name

    def get_composition(self):
        lst = []
        tmp = []
        res = '['
        for p in self.profiles:
            lst.append(p.profile_type.value)  # if p.profile_type.value not in lst else lst

        for p in self.profiles:
            if p.profile_type.value not in tmp:
                tmp.append(p.profile_type.value)
                res += ' ' + str(lst.count(p.profile_type.value)) + ' ' + p.profile_type.value + ','
        res = res[:len(res) - 1]
        res += ' ]'
        return res

    def add_profile(self, profile):
        if isinstance(profile, Profile):
            # Overwrite Storage profile if already exist
            if isinstance(profile, SimpleStorage):
                self.profiles = [p for p in self.profiles if not isinstance(p, SimpleStorage)]
            self.profiles.append(profile)
            if not self.to_optimize:
                if len(self.profiles) > 1:
                    self.to_optimize = True

        else:
            raise Exception('{} passed argument is not of type Profile'.format(profile))

    def set_profiles(self, profiles: [Profile]):
        try:
            for p in profiles:
                self.add_profile(p)
                if not self.to_optimize:
                    if len(self.profiles) > 1:
                        self.to_optimize = True
        except:
            raise Exception('Profiles is not iterable')

    def resolve(self, model_resolve_method=ModelResolveMethod.MINIMIZE_AND_MAXIMIZE, print_results=False,
                print_graphs=False, tee=False, pprint=False, per_allegra=False):

        if not self.to_optimize:
            return self

        self.resolve_method = model_resolve_method
        self.solver = None
        self.solver = Solver(self.profiles)

        self.solver.resolve(model_resolve_method, print_results, tee, pprint)
        self.__fix_flexibility_bounds()
        #self.__fix_baseline()

        if print_graphs:
            if model_resolve_method == ModelResolveMethod.MINIMIZE:
                self.print_graph('minimized')
            elif model_resolve_method == ModelResolveMethod.MAXIMIZE:
                self.print_graph('maximized')
            elif model_resolve_method == ModelResolveMethod.MINIMIZE_AND_MAXIMIZE:
                self.print_graph('minimized')
                self.print_graph('maximized')
                self.print_graph_2()

        if per_allegra:
            self.graphs_for_allegra()

        return self

    # Minimized Flexibility value cannot exceed Maximized Flexibility value
    def __fix_flexibility_bounds(self):
        for i in range(0, len(self.solver.results['maximized']['grid'])):
            self.solver.results['maximized']['grid'] = [x if x > y else y for x, y in
                                                        zip(self.solver.results['minimized']['grid'],
                                                            self.solver.results['maximized']['grid'])]

    # Baseline value cannot exceed Flexibility bounds (misscalculated because SimpleStorage has no baseline)
    def __fix_baseline(self):
        print(self.solver.results['baseline'])
        self.solver.results['baseline'] = [i if b > i else b for i, b in zip(self.solver.results['maximized']['grid'],
                                                                             self.solver.results['baseline'])]
        self.solver.results['baseline'] = [i if b < i else b for i, b in zip(self.solver.results['minimized']['grid'],
                                                                             self.solver.results['baseline'])]

    def needs_local_optimization(self):
        return self.to_optimize

    def get_flexibility(self, method):
        if not self.needs_local_optimization():
            p = self.profiles[0]
            return p.get_flexibility(method)
        else:
            if self.solver is None:
                print('This Pod has to be optimized. Run \'resolve()\' to get the flexibility.')
            else:
                return self.solver.results[method]['grid']

    def get_cost(self, method):
        if not self.needs_local_optimization():
            p = self.profiles[0]
            return [0] * 96,  # p.get_costs(method) TODO
        else:
            if self.solver is None:
                print('Before getting the costs you have to call \'resolve()\' and resolve the optimization.')
            else:
                return self.solver.results[method]['cost']

    def get_opt_time(self, method):
        if not self.needs_local_optimization():
            return '-'  # no time
        else:
            if self.solver is None:
                print('Before getting the costs you have to call \'resolve()\' and resolve the optimization.')
            else:
                return self.solver.results[method]['time']

    def get_costs_old(self):

        if self.solver is None:
            print('Before getting the costs you have to call \'resolve()\' and resolve the optimization.')
        else:
            if self.resolve_method == ModelResolveMethod.MINIMIZE:
                return self.solver.results[self.resolve_method]['cost']
            elif self.resolve_method == ModelResolveMethod.MAXIMIZE:
                return self.solver.results[self.resolve_method]['cost']
            elif self.resolve_method == ModelResolveMethod.MINIMIZE_AND_MAXIMIZE:
                return [self.solver.results['minimized']['cost'], self.solver.results['maximized']['cost']]

    def print_graph(self, method):
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.set(xlabel='Timestamp (t)', ylabel='Active Power (W)',
               title='Model Results - {} - {}'.format(method, self.solver.results[method]['solution_value']))
        plt.xticks(range(0, 96, 5))

        if self.solver.data['n_load_t1'] > 0:
            ax.plot(sum(l.profile for l in [p for p in self.solver.l1_array]), label='L1-Total')
        if self.solver.data['n_load_t2'] > 0:
            ax.plot(sum(l.profile for l in [p for p in self.solver.l2_array]), label='L2-Total')
            ax.plot(sum(l.profile for l in [p for p in self.solver.l2_array]) + np.array(
                self.solver.results[method]['load_t2_shift']).sum(axis=0), label='L2-Shifted')
        if self.solver.data['n_load_t3'] > 0:
            ax.plot(sum(l.profile for l in [p for p in self.solver.l3_array]), label='L3-Total')
            ax.plot(sum(l.profile for l in [p for p in self.solver.l3_array]) + np.array(
                self.solver.results[method]['load_t3_shift']).sum(axis=0), label='L3-Shifted')
        if self.solver.data['n_chp'] > 0:
            ax.plot(sum(chp.profile for chp in [p for p in self.solver.chp_array]), label='CHP-Total')
            ax.plot(sum(chp.profile for chp in [p for p in self.solver.chp_array]) + np.array(
                self.solver.results[method]['chp_shift']).sum(axis=0), label='CHP-Shifted')
        if self.solver.data['n_pv'] > 0:
            ax.plot(sum(l.profile for l in [p for p in self.solver.pv_array]), label='PV-Total')
            ax.plot(sum(l.profile for l in [p for p in self.solver.pv_array]) + np.array(
                self.solver.results[method]['pv_shift']).sum(axis=0), label='PV-Shifted')
        if self.solver.data['n_wind'] > 0:
            ax.plot(sum(l.profile for l in [p for p in self.solver.wind_array]), label='WIND-Total')
            ax.plot(sum(l.profile for l in [p for p in self.solver.wind_array]) + np.array(
                self.solver.results[method]['wind_shift']).sum(axis=0), label='WIND-Shifted')
        if self.solver.data['storage'] > 0:
            ax.plot(self.solver.results[method]['storage_charge'], label='Storage')

        # ax.plot(self.sum_shifted(method), label='Shifted')
        ax.plot(self.sum_baseline(), label='Total Baseline')

        ax.plot(self.solver.results[method]['grid'], label='Grid')
        plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=0.3)
        plt.show()

    def print_graph_2(self):

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.set(xlabel='Timestamp (t)', ylabel='Active Power (W)', title='Model Grid Results')
        plt.xticks(range(0, 96, 5))

        ax.plot(self.solver.results['minimized']['grid'], label='Grid (minimized)')
        ax.plot(self.solver.results['baseline'], label='Total Baseline')
        ax.plot(self.solver.results['maximized']['grid'], label='Grid (maximized)')
        plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=0.3)
        plt.show()

    def graphs_for_allegra(self):
        for index, p in enumerate(self.profiles):
            fig, ax = plt.subplots(figsize=(10, 7))
            plt.xticks(range(0, 96, 5))

            if isinstance(p, PV):
                ax.set(xlabel='Timestamp (t)', ylabel='Active Power (W)', title='PV Optimized')
                ax.plot(p.profile, label=str(str(p.profile_type) + str(index)))
                ax.plot(p.profile + self.solver.results['minimized']['pv_shift'][index], label='minimized')
                ax.plot(p.profile + self.solver.results['maximized']['pv_shift'][index], label='maximized')
            if isinstance(p, Wind):
                ax.set(xlabel='Timestamp (t)', ylabel='Active Power (W)', title='Wind Optimized')
                ax.plot(p.profile, label=str(str(p.profile_type) + str(index)))
                ax.plot(p.profile + self.solver.results['minimized']['wind_shift'][0], label='minimized')
                ax.plot(p.profile + self.solver.results['maximized']['wind_shift'][0], label='maximized')
            if isinstance(p, SimpleStorage):
                ax.set(xlabel='Timestamp (t)', ylabel='Active Power (W)', title='Storage Optimized')
                ax.plot(self.solver.results['minimized']['storage_charge'], label='minimized')
                ax.plot(self.solver.results['maximized']['storage_charge'], label='maximized')
            if isinstance(p, LoadT2):
                ax.set(xlabel='Timestamp (t)', ylabel='Active Power (W)', title='L2 Optimized')
                ax.plot(p.profile, label=str(str(p.profile_type) + str(index)))
                ax.plot(p.profile + self.solver.results['minimized']['load_t2_shift'][0], label='minimized')
                ax.plot(p.profile + self.solver.results['maximized']['load_t2_shift'][0], label='maximized')
            if isinstance(p, LoadT3):
                ax.set(xlabel='Timestamp (t)', ylabel='Active Power (W)', title='L3 Optimized')
                ax.plot(p.profile, label=str(str(p.profile_type) + str(index)))
                ax.plot(p.profile + self.solver.results['minimized']['load_t3_shift'][0], label='minimized')
                ax.plot(p.profile + self.solver.results['maximized']['load_t3_shift'][0], label='maximized')

            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.show()

    def sum_shifted(self, method):
        self.solver.results[method]['solution_value']
        shifted_list = []
        if self.solver.data['n_load_t1'] > 0:
            shifted_list.append(
                sum(l.profile for l in [p for p in self.solver.l1_array]))  # L1-Total - because l1 not shiftable
        if self.solver.data['n_load_t2'] > 0:
            shifted_list.append(sum(l.profile for l in [p for p in self.solver.l2_array]) + np.array(
                self.solver.results[method]['load_t2_shift']).sum(axis=0))  # L2-Shifted
        if self.solver.data['n_load_t3'] > 0:
            shifted_list.append(sum(l.profile for l in [p for p in self.solver.l3_array]) + np.array(
                self.solver.results[method]['load_t3_shift']).sum(axis=0))  # L3-Shifted
        if self.solver.data['n_chp'] > 0:
            shifted_list.append(sum(chp.profile for chp in [p for p in self.solver.chp_array]) + np.array(
                self.solver.results[method]['chp_shift']).sum(axis=0))  # CHP-Shifted
        if self.solver.data['n_pv'] > 0:
            shifted_list.append(sum(l.profile for l in [p for p in self.solver.pv_array]) - np.array(
                self.solver.results[method]['pv_shift']).sum(axis=0))  # PV-Shifted
        if self.solver.data['n_wind'] > 0:
            shifted_list.append(sum(l.profile for l in [p for p in self.solver.wind_array]) - np.array(
                self.solver.results[method]['wind_shift']).sum(axis=0))  # WIND-Shifted
        # if self.solver.data['storage'] > 0:
        # shifted_list.append([-1*x for x in self.solver.results[method]['storage_charge']]) # Storage

        shifted_total = [sum(x) for x in zip(*shifted_list)]
        return shifted_total

    def sum_baseline(self):
        baseline_list = []
        [baseline_list.append(p.profile) for p in self.profiles]
        baseline_total = [sum(x) for x in zip(*baseline_list)]
        return baseline_total
