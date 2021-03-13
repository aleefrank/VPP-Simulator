from src.pod import Pod


class LocalOptimizationResult(object):

    def __init__(self, date=None, data=None):
        if data is None:
            self.data = {
                'date': date,
                'optimizations': []
            }
        else:
            self.data = data

    def get_optimizations(self):
        return self.data['optimizations']

    def populate(self, pods: [Pod]):
        for pod in pods:
            element = {
                'baseline': pod.sum_baseline(),
                'name': pod.name,
                'composition': str(pod.get_composition()),
                'minimized': {
                    'flexibility': pod.get_flexibility('minimized'),
                    'cost': pod.get_cost('minimized'),
                    'time': pod.get_opt_time('minimized')
                },
                'maximized': {
                    'flexibility': pod.get_flexibility('maximized'),
                    'cost': pod.get_cost('maximized'),
                    'time': pod.get_opt_time('maximized')
                },
            }
            self.data['optimizations'].append(element)
