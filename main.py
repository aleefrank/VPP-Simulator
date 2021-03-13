import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.chp import CHP

sns.set()
from src.bess import Bess
from src.enums import ModelResolveMethod
from src.pontlab import Pontlab
from src.aggregator import Aggregator
from src.load import LoadT1, LoadT2, LoadT3
from src.pod import Pod
from src.pv import PV
from src.wind import Wind
from src.storage import SimpleStorage


####################################################################################
def print_graph(plant, title=''):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set(xlabel='Time', ylabel='Active Power (kW)', title=title)
    plt.xticks(range(0, 96, 5))

    ax.plot(plant.profile, label='Baseline', color='#bcbd22', linewidth=1)
    ax.plot(plant.get_flexibility('maximized'), label='Max', color='#ff7f0e')
    ax.plot(plant.get_flexibility('minimized'), label='Min', color='#1f77b4')
    # ax.plot(plant.min_shift, label='Min - shift')
    # ax.plot(plant.max_shift, label='Max - shift')
    plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=0.3)
    plt.show()


####################################################################################
np.random.seed(10)

scale_factor = 1
date = '2020-11-18'

pontlab1_test = np.load('Baseline/' + date + '.uvax.27.plants.1041.profile.baseline.npy')
pontlab2_test = np.load('Baseline/' + date + '.uvax.27.plants.1042.profile.baseline.npy')
load4_test = np.load('Baseline/' + date + '.uvax.27.plants.1043.profile.baseline.npy')
pv1_test = np.load('Baseline/' + date + '.uvax.27.plants.1044.profile.baseline.npy')
pv2_test = np.load('Baseline/' + date + '.uvax.27.plants.1045.profile.baseline.npy') / 10
wind1_test = np.load('Baseline/' + date + '.uvax.27.plants.1046.profile.baseline.npy')
wind2_test = np.load('Baseline/' + date + '.uvax.27.plants.1047.profile.baseline.npy')
load1_test = np.load('Baseline/' + date + '.uvax.27.plants.1048.profile.baseline.npy')
load2_test = np.load('Baseline/' + date + '.uvax.27.plants.1049.profile.baseline.npy')
load3_test = np.load('Baseline/' + date + '.uvax.27.plants.1050.profile.baseline.npy')
bess1_test = np.load('Baseline/' + date + '.uvax.27.plants.1051.profile.baseline.npy')
bess2_test = np.load('Baseline/' + date + '.uvax.27.plants.1052.profile.baseline.npy')
chp1_test = np.load('Baseline/' + date + '.uvax.27.plants.1054.profile.baseline.npy')

plot_tests = False
########################################################################################
#
#      SINGLE ELEMENT PODs
#
########################################################################################
# PV
pv1 = PV(pv1_test)  # max(kW) = 10 - day: center
pv2 = PV(pv2_test)  # max(kW) = 20 - day: center
p_pv1 = Pod(pv1)
p_pv2 = Pod(pv2)

# WIND
wind1 = Wind(wind1_test)  # max(kW) = 0.4 - day: center
wind2 = Wind(wind2_test)  # max(kW) = 0.8 - day: left
p_wind1 = Pod(wind1)
p_wind2 = Pod(wind2)
# CHP
chp1 = CHP(chp1_test, [x for x in list(range(0, 96)) if x not in list(range(0, 20))])  # max(kW) = 0.8 - day: center
p_chp1 = Pod(pv1)
# print_graph(chp1)

# BESS
bess1 = Bess(bess1_test)  # max(kW) = +-4
bess2 = Bess(bess2_test)  # max(kW) = +-4
p_bess1 = Pod(bess1)
p_bess2 = Pod(bess2)

# PONTLAB
pontlab1 = Pontlab(pontlab1_test)  # max(kW) = +-7
pontlab2 = Pontlab(pontlab2_test)  # max(kW) = +-6
p_pontlab1 = Pod(pontlab1)
p_pontlab2 = Pod(pontlab2)

# LOAD
load1 = LoadT1(load2_test)  # max(kW) = 0.0012 [no_shift - no_loss]
load2 = LoadT2(load1_test, list(range(0, 96)), 20)  # max(kW) = 0.06 [no_shift - loss]
load3 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))],
               1)  # max(kW) = 12 [shift - no_loss]
load4 = LoadT3(load4_test, [x for x in list(range(0, 96)) if x not in list(range(30, 45))],
               15)  # max(kW) = 11 [shift - loss]
p_load1 = Pod(load1)
p_load2 = Pod(load2)
p_load3 = Pod(load3)
p_load4 = Pod(load4)

if plot_tests:
    print_graph(pv1, 'PV_1')
    print_graph(pv2, 'PV_2')
    print_graph(wind1, 'WIND_1')
    print_graph(wind2, 'WIND_2')
    print_graph(bess1, 'BESS_1')
    print_graph(bess2, 'BESS_2')
    print_graph(pontlab1, 'PONTLAB_1')
    print_graph(pontlab2, 'PONTLAB_2')
    print_graph(load1, 'LOAD_1 - T1 [No_shift - No_loss]')
    print_graph(load2, 'LOAD_2 - T2 [No_shift - loss]')
    print_graph(load3, 'LOAD_3 - T3 [shift - No_loss]')
    print_graph(load4, 'LOAD_4 - T3 [shift - loss]')

########################################################################################
#
#      MIXED ELEMENTS PODs
#
########################################################################################
#  CONF_1: 1wind,              1L2
#  CONF_2: 1PV,1St,            1L3
#  CONF_3: 1PV,1St,            1L2,1L3
#  CONF_4: 1PV,1wind,1St,      2L2,1L3
#  CONF_5: 2PV,2wind,1chp,1St,      1L1,3L2,2L3
#  CONF_6: 3PV,3wind,1St,      3l1,3L2,3L3
#  CONF_7: 5PV,5wind,1St,      3l1,5L2,5L3
########################################################################################

# CONF_1    ->     [ 1 WIND / 1 L2 ]
p1 = Pod()
p1_wind_1 = Wind(wind1_test)

p1_l2_1 = LoadT2(load1_test, list(range(0, 96)), 25)  # [no_shift - loss]
p1.set_profiles([p1_wind_1, p1_l2_1])

########################################################################################
# CONF_2    ->     [1 PV / 1 St / 1 L3 ]
p2 = Pod()
p2_pv_1 = PV(pv1_test)
p2_st = SimpleStorage(70)

p2_l3_1 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))], 1)  # [shift - no_loss]
p2.set_profiles([p2_pv_1, p2_st,
                 p2_l3_1])
########################################################################################
# CONF_3    ->     [1 PV / 1 St / 1 L2 / 1 L3 ]
p3 = Pod()
p3_pv_1 = PV(pv1_test)
p3_st = SimpleStorage(70)

p3_l2_1 = LoadT2(load1_test, list(range(0, 96)), 25)  # [no_shift - loss]
p3_l4_1 = LoadT3(load4_test, [x for x in list(range(0, 96)) if x not in list(range(30, 45))], 15)  # [shift - loss]
p3.set_profiles([p3_pv_1, p3_st,
                 p3_l2_1,
                 p3_l4_1])
########################################################################################
# CONF_4    ->     [1 PV / 1 WIND / 1 St / 2 L2 / 1 L3 ]
p4 = Pod()
p4_pv_1 = PV(pv1_test)  # max(kW) = 10 - day: center
p4_wind_1 = Wind(wind1_test)  # max(kW) = 0.4 - day: center
p4_st = SimpleStorage(70)

p4_l2_1 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p4_l2_2 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p4_l3_1 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))], 1)  # [shift - no_loss]
p4.set_profiles([p4_pv_1, p4_wind_1, p4_st,
                 p4_l2_1, p4_l2_2,
                 p4_l3_1])
########################################################################################
# CONF_5    ->     [2 PV / 2 WIND / 1 CHP / 1 ST / 1 L1 / 3 L2 / 2 L3 (l4)]
p5 = Pod()
p5_pv_1 = PV(pv1_test)  # max(kW) = 10 - day: center
p5_pv_2 = PV(pv1_test)  # max(kW) = 10 - day: center
p5_wind_1 = Wind(wind1_test)  # max(kW) = 0.4 - day: center
p5_wind_2 = Wind(wind2_test)  # max(kW) = 0.8 - day: center
p5_chp_1 = CHP(chp1_test,
               [x for x in list(range(0, 96)) if x not in list(range(0, 20))])  # max(kW) = 0.8 - day: center
p5_st = SimpleStorage(70)

p5_l1_1 = LoadT1(load2_test)  # max(kW) = 0.06 [no_shift - no_loss]
p5_l2_1 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p5_l2_2 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p5_l2_3 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p5_l3_1 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))], 1)  # [shift - no_loss]
p5_l3_2 = LoadT3(load4_test, [x for x in list(range(0, 96)) if x not in list(range(30, 45))], 15)  # [shift - loss]
p5.set_profiles([p5_pv_1, p5_pv_2, p5_wind_1, p5_wind_2, p5_chp_1, p5_st,
                 p5_l1_1,
                 p5_l2_1, p5_l2_2, p5_l2_3,
                 p5_l3_1, p5_l3_2
                 ])

########################################################################################
# CONF_6    ->     [3 PV / 3 WIND / 1 ST / 3 L1 / 3 L2 / 3 L3 (l4)]
p6 = Pod()
p6_pv_1 = PV(pv1_test)  # max(kW) = 10 - day: center
p6_pv_2 = PV(pv1_test)  # max(kW) = 10 - day: center
p6_pv_3 = PV(pv1_test)  # max(kW) = 10 - day: center
p6_wind_1 = Wind(wind1_test)  # max(kW) = 0.4 - day: center
p6_wind_2 = Wind(wind1_test)  # max(kW) = 0.4 - day: center
p6_wind_3 = Wind(wind2_test)  # max(kW) = 0.8 - day: center
p6_st = SimpleStorage(70)

p6_l1_1 = LoadT1(load2_test)  # max(kW) = 0.06 [no_shift - no_loss]
p6_l1_2 = LoadT1(load2_test)  # max(kW) = 0.06 [no_shift - no_loss]
p6_l1_3 = LoadT1(load2_test)  # max(kW) = 0.06 [no_shift - no_loss]
p6_l2_1 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p6_l2_2 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p6_l2_3 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p6_l3_1 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))], 1)  # [shift - no_loss]
p6_l3_2 = LoadT3(load4_test, [x for x in list(range(0, 96)) if x not in list(range(30, 45))], 15)  # [shift - loss]
p6_l3_3 = LoadT3(load4_test, [x for x in list(range(0, 96)) if x not in list(range(30, 45))], 15)  # [shift - loss]
p6.set_profiles([p6_pv_1, p6_pv_2, p6_pv_3, p6_wind_1, p6_wind_2, p6_wind_3, p6_st,
                 p6_l1_1, p6_l1_2, p6_l1_3,
                 p6_l2_1, p6_l2_2, p6_l2_3,
                 p6_l3_1, p6_l3_2, p6_l3_3
                 ])

########################################################################################
# CONF_7    ->     [5 PV / 5 WIND / 1 ST / 3 L1 / 5 L2 / 5 L3]
p7 = Pod()
p7_pv_1 = PV(pv1_test)  # max(kW) = 10 - day: center
p7_pv_2 = PV(pv1_test)  # max(kW) = 10 - day: center
p7_pv_3 = PV(pv1_test)  # max(kW) = 10 - day: center
p7_pv_4 = PV(pv1_test)  # max(kW) = 10 - day: center
p7_pv_5 = PV(pv1_test)  # max(kW) = 10 - day: center
p7_wind_1 = Wind(wind1_test)  # max(kW) = 0.4 - day: center
p7_wind_2 = Wind(wind1_test)  # max(kW) = 0.4 - day: center
p7_wind_3 = Wind(wind2_test)  # max(kW) = 0.8 - day: center
p7_wind_4 = Wind(wind2_test)  # max(kW) = 0.8 - day: center
p7_wind_5 = Wind(wind2_test)  # max(kW) = 0.8 - day: center
p7_st = SimpleStorage(70)

p7_l1_1 = LoadT1(load2_test)  # max(kW) = 0.06 [no_shift - no_loss]
p7_l1_2 = LoadT1(load2_test)  # max(kW) = 0.06 [no_shift - no_loss]
p7_l1_3 = LoadT1(load2_test)  # max(kW) = 0.06 [no_shift - no_loss]
p7_l2_1 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p7_l2_2 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p7_l2_3 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p7_l2_4 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p7_l2_5 = LoadT2(load1_test, list(range(0, 96)), 25)  # max(kW) = 0.0012 [no_shift - loss]
p7_l3_1 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))], 1)  # [shift - no_loss]
p7_l3_2 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))], 1)  # [shift - no_loss]
p7_l3_3 = LoadT3(load3_test, [x for x in list(range(0, 96)) if x not in list(range(15, 25))], 1)  # [shift - no_loss]
p7_l3_4 = LoadT3(load4_test, [x for x in list(range(0, 96)) if x not in list(range(30, 45))], 15)  # [shift - loss]
p7_l3_5 = LoadT3(load4_test, [x for x in list(range(0, 96)) if x not in list(range(30, 45))], 15)  # [shift - loss]
p7.set_profiles(
    [p7_pv_1, p7_pv_2, p7_pv_3, p7_pv_4, p7_pv_5, p7_wind_1, p7_wind_2, p7_wind_3, p7_wind_4, p7_wind_5, p7_st,
     p7_l1_1, p7_l1_2, p7_l1_3,
     p7_l2_1, p7_l2_2, p7_l2_3, p7_l2_4, p7_l2_5,
     p7_l3_1, p7_l3_2, p7_l3_3, p7_l3_4, p7_l3_5
     ])
########################################################################################

solver_method = ModelResolveMethod.MINIMIZE_AND_MAXIMIZE
# p1.resolve(print_results=True, print_graphs=True, tee=False, pprint=False, per_allegra=False)  # OK
# p2.resolve(print_results=True, print_graphs=True, tee=False, pprint=False, per_allegra=False) # OK
# p3.resolve(print_results=True, print_graphs=True, tee=False, pprint=False, per_allegra=False) # OK
# p4.resolve(print_results=True, print_graphs=True, tee=False, pprint=False, per_allegra=False)
# p5.resolve(print_results=False, print_graphs=True, tee=False, pprint=False, per_allegra=False) # OK
# p6.resolve(print_results=False, print_graphs=True, tee=False, pprint=False, per_allegra=False) # OK
# p7.resolve(print_results=False, print_graphs=True, tee=False, pprint=False, per_allegra=False) # OK

#################################################################
#
#   TEST AGGEREGATOR
#
##################################################################

aggregator = Aggregator()

n_p_pv1 = 2
n_p_pv2 = 0
n_p_wind1 = 4
n_p_wind2 = 0
n_p_chp1 = 0
n_p_bess1 = 0
n_p_bess2 = 0
n_p_pontlab1 = 0
n_p_pontlab2 = 0
n_p_load1 = 0
n_p_load2 = 2
n_p_load3 = 2
n_p_load4 = 2

n_p1 = 0
n_p2 = 0
n_p3 = 2
n_p4 = 0
n_p5 = 0
n_p6 = 0
n_p7 = 0

test_configuration = [p_pv1] * n_p_pv1 + [p_pv2] * n_p_pv2 + \
                     [p_wind1] * n_p_wind1 + [p_wind2] * n_p_wind2 + \
                     [p_chp1] * n_p_chp1 + \
                     [p_bess1] * n_p_bess1 + [p_bess2] * n_p_bess2 + \
                     [p_pontlab1] * n_p_pontlab1 + [p_pontlab2] * n_p_pontlab2 + \
                     [p_load1] * n_p_load1 + [p_load2] * n_p_load2 + [p_load3] * n_p_load3 + [p_load4] * n_p_load4 + \
                     [p1] * n_p1 + [p2] * n_p2 + [p3] * n_p3 + [p4] * n_p4 + [p5] * n_p5 + [p6] * n_p6 + [p7] * n_p7

aggregator.set_pods(test_configuration)

aggregator.resolve_pods_and_aggregate(print_results=True,
                                      print_graphs=True)

# Scaling Analysis plot
n_pods = [10, 20, 30, 60, 100, 140, 200]
ser = [0.67, 3.24, 3.58, 8.63, 14.86, 27.71, 31.61]
par = [0.67, 0.72, 0.92, 1.01, 1.67, 1.88, 2.1]


def plot_results(pods, ser, par):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set(xlabel='Number of PODs', ylabel='Total Optimization Time (s)', title='Performance of the Model')

    ax.plot(pods, ser, color='r', label='Sequential')
    ax.plot(pods, par, label='Parallel')

    plt.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=0.3)
    plt.show()


plot_results(n_pods, ser, par)
