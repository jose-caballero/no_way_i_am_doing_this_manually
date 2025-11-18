import logging
import inspect


#
# class to help creating a logger dynamically
# for the plugins (e.g. hvicinga), we want the logger name to be like this
#       hypervisormanager:<hypervisor_nmame>.hvicinga
# but we don't know in each case the exact logger name from hypervisormanager,
# as it changes for each case. 
# This class finds that out, and just add ".hvicinga" (or whatever) to the logger name
#


class SetLogger:
    def _set_logger(self, default="default"):
        caller_logger = None

        # Walk up the call stack to find a frame with a `self.log` logger instance
        for frame_info in inspect.stack()[1:]:
            frame = frame_info.frame
            if 'self' in frame.f_locals:
                caller_instance = frame.f_locals['self']
                if hasattr(caller_instance, 'log') and isinstance(caller_instance.log, logging.Logger):
                    caller_logger = caller_instance.log.name
                    break

        logger_name = f"{caller_logger}.{self.__class__.__name__.lower()}" if caller_logger else default
        self.log = logging.getLogger(logger_name)
        #self.log.debug(f'Logger {logger_name} initialized.')


