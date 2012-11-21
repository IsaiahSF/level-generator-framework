from progressobserver import ProgressObserver

## Interface for classes to which ProgressObserver instances can be
#  attached.
class ProgressSubject:
    ## Constructor
    def __init__(self):
        ## list of listeners implementing ProgressObserver
        self.listeners = []
        ## Float between 0.0 and 1.0 inclusive. Don't set directly! Use
        #  setProgress()
        self.progress = 0.0
        ## Brief human-readable status string. Don't set directly! Use
        #  setStatus()
        self.status = ''
        
    ## Add a listener object to receive progress data from the level generation
    #  process.
    #
    #  @param listener object that implements ProgressObserver
    def addListener(self, listener):
        if not issubclass(listener.__class__, ProgressObserver):
            raise TypeError("listener is not a subclass of ProgressObserver")
        listener.setProgress(self.progress)
        listener.setStatus(self.status)
        self.listeners.append(listener)

    ## update all listeners using the ProgressObserver.write() method
    def listenerWrite(self, string):
        assert type(string) == str
        for l in self.listeners:
            l.write(string)

    ## update all listeners using the ProgressObserver.setProgress() method
    def setProgress(self, progress):
        assert progress >= 0.0
        assert progress <= 1.0
        self.progress = progress
        for l in self.listeners:
            l.setProgress(self.progress)
        
    ## update all listeners using the ProgressObserver.setStatus() method
    def setStatus(self, status):
        assert type(status) == str
        self.status = status
        for l in self.listeners:
            l.setStatus(self.status)
