from multiprocessing import Pool
from multiprocessing import set_start_method


class Multiprocess:

    def __init__(self, num_processes, target, args):
        self.num_processes = num_processes
        self.target = target
        self.args = args

    def run(self):
        set_start_method('fork')
        results = []
        with Pool(processes=self.num_processes) as pool:
            results.extend(pool.map(self.target, self.args))
        return results
