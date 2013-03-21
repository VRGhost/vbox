"""Vm power state maneger - running, off, saved, etc."""

from . import base

class State(object):

    vm = None
    cli = property(lambda s: s.vm.cli)

    pause = lambda s: s.cli.manage.controlvm.pause(s.vm.name)
    resume = lambda s: s.cli.manage.controlvm.resume(s.vm.name)
    reset = lambda s: s.cli.manage.controlvm.reset(s.vm.name)
    powerOff = lambda s, *a, **kw: s.vm.powerOff(*a, **kw)
    start = lambda s, *a, **kw: s.vm.start(*a, **kw)

    knownStates = (
        "running", "paused", "poweroff",
        "aborted",
    )

    def __init__(self, vm):
        super(State, self).__init__()
        self.vm = vm

    @property
    def val(self):
        rv = self.vm.getProp("VMState")
        assert rv in self.knownStates, repr(rv)
        return rv

    for name in knownStates:
        locals()[name] = (lambda X: property(lambda s: s.val == X))(name)
    del name