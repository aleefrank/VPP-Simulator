from flask import Flask, request
from src.aggregator import Aggregator
from src.local_optimization_result import LocalOptimizationResult
import json
import numpy as np
from flask import jsonify

from apis_utils import subdict, searchbyId, load_baseline, init_aggregator, get_uvam_by_id

np.random.seed(10)
app = Flask(__name__)


"""
api functions
"""


@app.route('/')
@app.route('/api/<int:uvamId>/getInfo', methods=['GET', 'POST'])
def get_info(uvamId):
    if request.method == 'GET':
        mask = ['id', 'name', 'description']
        plants = {'uvamid': uvamId,
                  'data': []}
        uvam = get_uvam_by_id(uvamId)
        [plants['data'].append(subdict(i, mask)) for i in uvam['plants']]

        return jsonify(plants)


@app.route('/api/<int:uvamId>/readProfiles', methods=['POST'])
def read_profiles(uvamId):
    config = request.json
    plants = {'data': [],
              'date': '2020-11-01'  # config['date']
              }
    uvam = get_uvam_by_id(uvamId)
    for x in config['plants']:
        el = searchbyId(x['id'], uvam['plants']).copy()
        el['name'] = x['name']
        # if el['type'] == 'MIX':
        for sub_el in el['components']:
            if sub_el['type'] != 'SIMPLE_STORAGE':
                sub_el['baseline'] = load_baseline(sub_el, plants['date'])
        # else:
        #    el['baseline'] = load_baseline(el, plants['date'])
        el['quantity'] = x['quantity']
        plants['data'].append(el)

    return jsonify(plants)


@app.route('/api/runLocalOptimization', methods=['POST'])
def local_optimization():
    content = request.json
    aggregator = Aggregator()
    init_aggregator(aggregator, content)

    aggregator.resolve_pods_multiprocessing()
    local_opt_result = LocalOptimizationResult(date=content['date'])
    local_opt_result.populate(aggregator.pods)
    return jsonify(local_opt_result.__dict__)


@app.route('/api/runAggregatedOptimization', methods=['POST'])
def aggregate():
    content = request.json
    r = {'data': None}
    local_opt_result = LocalOptimizationResult(**json.loads(content))
    aggregator = Aggregator()
    aggregator.set_local_opt_result(local_opt_result)
    result = aggregator.aggregate()
    r['data'] = result
    return jsonify(r)


@app.route('/api/runLocalAndAggregatedOptimization', methods=['POST'])
def optimize_and_aggregate():
    content = request.json
    aggregator = Aggregator()
    init_aggregator(aggregator, content)

    result = aggregator.resolve_pods_and_aggregate()
    return jsonify(result)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=4996)
