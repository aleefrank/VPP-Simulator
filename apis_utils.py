import os
from operator import itemgetter

from src.bess import Bess
from src.chp import CHP
from src.load import LoadT1, LoadT2, LoadT3
from src.pod import Pod
from src.pontlab import Pontlab
from src.pv import PV
from src.wind import Wind
from src.storage import SimpleStorage
import json
import numpy as np

np.random.seed(10)
scale_factor = 1000  # 1000000

########################################################

platform = {
    'uvams': [
        {'id': 27,
         'plants': [
             {'id': 1044,
              'name': 'PV_1',
              'type': 'PV',
              'description': 'Photovoltaic Plant',
              'components': [
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None}
              ]},
             {'id': 1045,
              'name': 'PV_2',
              'type': 'PV',
              'description': 'Photovoltaic Plant',
              'components': [
                  {'id': 1045,
                   'name': 'PV_2',
                   'type': 'PV',
                   'baseline': None}
              ]},
             {'id': 1046,
              'name': 'WIND_1',
              'type': 'WIND',
              'description': 'Wind Plant',
              'components': [
                  {'id': 1046,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None}
              ]},
             {'id': 1047,
              'name': 'WIND_2',
              'type': 'WIND',
              'description': 'Wind Plant',
              'components': [
                  {'id': 1047,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None}
              ]},
             {'id': 1054,
              'name': 'CHP_1',
              'type': 'CHP',
              'description': 'Combined Heat and Power Plant',
              'components': [
                  {'id': 1054,
                   'name': 'CHP_1',
                   'type': 'CHP',
                   'baseline': None}
              ]},
             {'id': 1048,
              'name': 'LOAD_1',
              'type': 'LOAD_T2',
              'description': 'Type 2 Load - [no_shift - loss]',
              'components': [
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None}
              ]},
             {'id': 1049,
              'name': 'LOAD_2',
              'type': 'LOAD_T1',
              'description': 'Type 1 Load - [no_shift - no_loss]',
              'components': [
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None}
              ]},
             {'id': 1050,
              'name': 'LOAD_3',
              'type': 'LOAD_T3',
              'description': 'Type 3 Load - [shift - no_loss]',
              'components': [
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]},
             {'id': 1043,
              'name': 'LOAD_4',
              'type': 'LOAD_T3',
              'description': 'Type 3 Load - [shift - loss]',
              'components': [
                  {'id': 1043,
                   'name': 'LOAD_4',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]},
             {'id': 1051,
              'name': 'BESS_1',
              'type': 'BESS',
              'description': 'Storage',
              'components': [
                  {'id': 1051,
                   'name': 'BESS_1',
                   'type': 'BESS',
                   'baseline': None}
              ]},
             {'id': 1052,
              'name': 'BESS_2',
              'type': 'BESS',
              'description': 'Storage',
              'components': [
                  {'id': 1052,
                   'name': 'BESS_2',
                   'type': 'BESS',
                   'baseline': None}
              ]},
             {'id': 1041,
              'name': 'PONTLAB_1',
              'type': 'PONTLAB',
              'description': 'Trigeneration Plant',
              'components': [
                  {'id': 1041,
                   'name': 'PONTLAB_1',
                   'type': 'PONTLAB',
                   'baseline': None}
              ]},
             {'id': 1042,
              'name': 'PONTLAB_2',
              'type': 'PONTLAB',
              'description': 'Trigeneration Plant',
              'components': [
                  {'id': 1042,
                   'name': 'PONTLAB_2',
                   'type': 'PONTLAB',
                   'baseline': None}
              ]},
             {'id': 1000,
              'name': 'CONF_1',
              'type': 'MIX',
              'description': 'Mixed Configuration - [ WIND - LOAD_T2 ]',
              'components': [
                  {'id': 1046,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None}
              ]},
             {'id': 2000,
              'name': 'CONF_2',
              'type': 'MIX',
              'description': 'Mixed Configuration - [ PV - SIMPLE_STORAGE - LOAD_T3 ]',
              'components': [
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1053,
                   'name': 'STORAGE_2',
                   'type': 'SIMPLE_STORAGE',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]},
             {'id': 3000,
              'name': 'CONF_3',
              'type': 'MIX',
              'description': 'Mixed Configuration - [ PV - SIMPLE_STORAGE - LOAD_T2 - LOAD_T3 ]',
              'components': [
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1053,
                   'name': 'STORAGE_3',
                   'type': 'SIMPLE_STORAGE',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]},
             {'id': 4000,
              'name': 'CONF_4',
              'type': 'MIX',
              'description': 'Mixed Configuration - [ PV - SIMPLE_STORAGE - 2 LOAD_T2 - LOAD_T3 ]',
              'components': [
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1053,
                   'name': 'STORAGE_3',
                   'type': 'SIMPLE_STORAGE',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]},
             {'id': 5000,
              'name': 'CONF_5',
              'type': 'MIX',
              'description': 'Mixed Configuration - [ 2 PV - 2 WIND - 1 CHP - SIMPLE_STORAGE - 1 LOAD_T1 - 3 LOAD_T2 - 2 LOAD_T3 ]',
              'components': [
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1046,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1047,
                   'name': 'WIND_2',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1054,
                   'name': 'CHP_1',
                   'type': 'CHP',
                   'baseline': None},
                  {'id': 1053,
                   'name': 'STORAGE_3',
                   'type': 'SIMPLE_STORAGE',
                   'baseline': None},
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_4',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]},
             {'id': 6000,
              'name': 'CONF_6',
              'type': 'MIX',
              'description': 'Mixed Configuration - [ 2 PV - 3 WIND - SIMPLE_STORAGE - 3 LOAD_T1 - 3 LOAD_T2 - 3 LOAD_T3 ]',
              'components': [
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1046,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1046,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1047,
                   'name': 'WIND_2',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1053,
                   'name': 'STORAGE_3',
                   'type': 'SIMPLE_STORAGE',
                   'baseline': None},
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None},
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None},
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_4',
                   'type': 'LOAD_T3',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_4',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]},
             {'id': 7000,
              'name': 'CONF_7',
              'type': 'MIX',
              'description': 'Mixed Configuration - [ 3 PV - 5 WIND - SIMPLE_STORAGE - 3 LOAD_T1 - 5 LOAD_T2 - 5 LOAD_T3 ]',
              'components': [
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1044,
                   'name': 'PV_1',
                   'type': 'PV',
                   'baseline': None},
                  {'id': 1046,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1046,
                   'name': 'WIND_1',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1047,
                   'name': 'WIND_2',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1047,
                   'name': 'WIND_2',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1047,
                   'name': 'WIND_2',
                   'type': 'WIND',
                   'baseline': None},
                  {'id': 1053,
                   'name': 'STORAGE_3',
                   'type': 'SIMPLE_STORAGE',
                   'baseline': None},
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None},
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None},
                  {'id': 1049,
                   'name': 'LOAD_2',
                   'type': 'LOAD_T1',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1048,
                   'name': 'LOAD_1',
                   'type': 'LOAD_T2',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_3',
                   'type': 'LOAD_T3',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_4',
                   'type': 'LOAD_T3',
                   'baseline': None},
                  {'id': 1050,
                   'name': 'LOAD_4',
                   'type': 'LOAD_T3',
                   'baseline': None}
              ]}
         ]}
    ]
}


########################################################
def serialize(obj):
    def check(o):
        for k, v in o.__dict__.items():
            try:
                _ = json.dumps(v)
                o.__dict__[k] = v
            except TypeError:
                o.__dict__[k] = str(v)
        return o

    return json.dumps(check(obj).__dict__, indent=2)


def subdict(d, ks):
    vals = []
    if len(ks) >= 1:
        vals = itemgetter(*ks)(d)
        if len(ks) == 1:
            vals = [vals]
    return dict(zip(ks, vals))


def get_uvam_by_id(uvamid):
    uvam = None
    for i in platform['uvams']:
        if i['id'] == uvamid:
            uvam = i
            return uvam
    return uvam

def searchbyId(id, dictlist):
    return [element for element in dictlist if element['id'] == id][0]


def load_baseline(tmp, date):
    list_of_files = os.listdir('Baseline')
    for f in list_of_files:
        if f.startswith(date) and f.__contains__(
                str(tmp['id'])):  # since its all type str you can simply use startswith
            tmp['baseline'] = [x for x in np.load('Baseline/' + f).tolist()]
            break
    return tmp['baseline']


def load_profile(element):
    profile = None
    if element['type'] == 'PV':
        if element['name'] == 'PV_2':
            profile = PV(np.array(element['baseline']), scale_factor=0.1)
        else:
            profile = PV(np.array(element['baseline']))
    if element['type'] == 'WIND':
        profile = Wind(np.array(element['baseline']))
    if element['type'] == 'CHP':
        profile = CHP(np.array(element['baseline']), [x for x in list(range(0, 96)) if x not in list(range(0, 20))])  # max(kW) = 0.8 - day: center
    if element['type'] == 'BESS':
        profile = Bess(np.array(element['baseline']))
    if element['type'] == 'PONTLAB':
        profile = Pontlab(np.array(element['baseline']))
    if element['type'] == 'SIMPLE_STORAGE':
        profile = SimpleStorage(70)
    if element['type'] == 'LOAD_T1':
        profile = LoadT1(np.array(element['baseline']))  # [no_shift - no_loss]
    if element['type'] == 'LOAD_T2':
        profile = LoadT2(np.array(element['baseline']), list(range(0, 96)), 25)  # [no_shift - loss]
    if element['type'] == 'LOAD_T3':
        if element['name'] == 'LOAD_4':
            profile = LoadT3(np.array(element['baseline']),
                             [x for x in list(range(0, 96)) if x not in list(range(30, 45))], 20)  # [shift - loss]
        else:
            profile = LoadT3(np.array(element['baseline']),
                             [x for x in list(range(0, 96)) if x not in list(range(50, 70))],
                             10)  # [shift - no_loss]
    return profile


def init_aggregator(aggregator, content):
    for element in content['plants']:
        vars()[element['name']] = Pod(name=element['name'])
        # if element['type'] == 'MIX':
        for c in element['components']:
            profile = load_profile(c)
            if profile != None:
                vars()[element['name']].add_profile(profile)
        # else:
        #    profile = load_profile(element)
        #    if profile != None:
        #        vars()[element['name']].add_profile(profile)

        aggregator.add_pod(vars()[element['name']])
