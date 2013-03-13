import subprocess

class Popen(subprocess.Popen):
    """Popen class that executes python callable when called process finishes."""

    def __init__(self, *args, **kwargs):
        self._returnHandle = kwargs.pop("onFinish", None)
        super(Popen, self).__init__(*args, **kwargs)

    _realReturnCode = None
    def returncode():
        doc = "The returncode property."
        def fget(self):
            return self._realReturnCode
        def fset(self, value):
            self._realReturnCode = value
            if (value is not None) and self._returnHandle:
                self._returnHandle(self)
        return locals()
    returncode = property(**returncode())