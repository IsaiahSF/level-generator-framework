## Defines interface for ProgressObservers
#
#  This class is an interface. It defines required functions for a class to
#  implement ProgressObserver. This is how a class that implements Executor
#  or Generator provides feedback on map compilation.
class ProgressObserver:

    ## Console output gets directed here
    #
    #  Should behave like writing to stdout. No inserting newlines.
    #
    #  @param string (Short) string to update console output
    def write(self, string):
        raise NotImplementedError()

    ## Receives an overall progress metric
    #
    #  @param progress Float between 0.0 and 1.0 inclusive
    def setProgress(self, progress):
        raise NotImplementedError()

    ## Receives string describing current task or status of compilation.
    #
    #  @param status Brief human-readable status string
    def setStatus(self, status):
        raise NotImplementedError()
