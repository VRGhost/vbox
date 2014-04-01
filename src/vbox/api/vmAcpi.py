from . import (
    base,
    exceptions,
    props,
)

class ACPI(base.SubEntity):
    """ACPI control for the virtual machine."""

    enabled = props.OnOff(**props.modify("acpi"))

    def powerButton(self):
        """Simulate ACPI power button press."""
        self.source.acpiPowerButton()

    def sleepButton(self):
        """Simulate ACPI power button press."""
        self.source.acpiSleepButton()

    def __nonzero__(self):
        """This object evaluates to 'True' when the ACPI is enabled."""
        return self.enabled