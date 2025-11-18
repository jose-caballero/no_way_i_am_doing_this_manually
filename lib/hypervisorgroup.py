import threading

class HyperVisorGroup(list):
    
    def __init__(self, migration_manager):
        self.migration_manager = migration_manager
        super(HyperVisorGroup, self).__init__()

    def run(self, step, parallel=False):
        if parallel == True:
            self._run_parallel(step)
        else:
            self._run_series(step)

    def _run_series(self, step):
        """
        process each HyperVisor in series for a given step
        """
        for hv in self.__iter__():
            hv.run(step)

    def _run_parallel(self, step):
        """
        process all HyperVisors in parallel for a given step
        """
        threads = []
        for hv in self.__iter__():
            thread = threading.Thread(target=hv.run, args=(step,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()


