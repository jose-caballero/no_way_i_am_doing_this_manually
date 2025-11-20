import threading

class HyperVisorGroup(list):

    def __init__(self, migration_manager):
        self.migration_manager = migration_manager
        super(HyperVisorGroup, self).__init__()

    def run(self, step):
        if step == "setup":
            self._run_parallel(step)
        elif step == "pre_drain":
            self._run_parallel(step)
        elif step == "pre_reinstall":
            self._run_parallel(step)
        elif step == "post_reinstall":
            self._run_parallel(step)
        elif step == "noops":
            self._run_parallel(step)

    def _run_series(self, step):
        """
        process each HyperVisor in series for a given step
        """
        for hv in self.__iter__():
            getattr(hv, step)()

    def _run_parallel(self, step):
        """
        process all HyperVisors in parallel for a given step
        """
        threads = []
        for hv in self.__iter__():
            thread = threading.Thread(target=getattr(hv, step))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
