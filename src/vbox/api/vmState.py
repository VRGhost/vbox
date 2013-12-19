import time

from . import (
    base,
    props,
    exceptions,
)

def StateChangeCall(fn, targetState, timeout=10):
    def _wrapper(self):
        vm = self.source
        origState = self.val
        if origState == targetState:
            # Already operationa;
            return

        endTime = time.time() + timeout
        rv = fn(self) # Actual functional callback

        vm.clearCache()
        while time.time() < endTime:
            time.sleep(0.2)
            vm.clearCache()
            if self.val not in (origState, targetState):
                raise exceptions.StateTransitionError("Unexpected vm state: {!r}".format(self.val))
            if self.val == targetState:
                break
        else:
            if self.val != targetState:
                raise exceptions.StateTransitionError("Unable to transition to the {!r} (current state: {!r}).".format(
                    targetState, self.val,
                ))

        return rv

    _wrapper.__name__ = "StateChange::{}".format(targetState)
    return _wrapper

class State(base.SubEntity):

    vm = None
    cli = property(lambda s: s.vm.cli)

    pause = StateChangeCall(
        lambda s: s.source.pause(),
        "paused",
    )
    resume = StateChangeCall(
        lambda s: s.source.resume(),
        "running",
    )
    reset = StateChangeCall(
        lambda s: s.source.reset(),
        "running",
    )
    powerOff = StateChangeCall(
        lambda s: s.source.poweroff(),
        "poweroff",
    )
    start = StateChangeCall(
        lambda s, **kw: s.source.start(**kw),
        "running",
    )

    # Mutable state is when hardware parameters of VM can be changed.
    mutable = property(lambda s: s.val in ("poweroff", "aborted"))

    knownStates = (
        None, # VirtualBox was not ready to provide valid vm info.
        "running", "paused", "poweroff",
        "aborted", "stopping", "saved",
    )

    @props.SourceProperty
    def val(self):
        try:
            rv = self.source.info.get("VMState")
        except self.source.cli.exceptions.ParsedVboxError as err:
            if err.errorName == "E_ACCESSDENIED":
                rv = None
            else:
                raise

        assert rv in self.knownStates, repr(rv)
        return rv

    for name in knownStates:
        if name:
            locals()["is{}".format(name.title())] = (lambda X: (lambda s: s.val == X))(name)
    del name