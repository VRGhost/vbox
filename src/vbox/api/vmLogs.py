"""VM log accessing object."""

import glob
import os

from . import (
    base,
    props,
    exceptions,
)

class Logs(base.SubEntity):
    """Log collection object."""

    directory = props.Str(lambda s: s.source.info["LogFldr"])

    def latest(self):
        """Return path to the latest VM logfile."""
        return self[0]

    def __getitem__(self, idx):
        return self._listFiles()[idx]

    def __len__(self):
        return len(self._listFiles())

    def _listFiles(self):
        """List log files in the log directory.

        The newest log file is to have index 0.
        """
        fnames = []
        for fname in glob.glob(os.path.join(
            self.directory,
            "VBox.log*"
        )):
            strIdx = fname.rsplit('.', 1)[-1]
            try:
                idx = int(strIdx)
            except ValueError:
                assert strIdx == "log" # newest log file lacks numeric extension.
                idx = 0
            fnames.append((idx, fname))

        fnames.sort(key=lambda el: el[0])
        return tuple(el[1] for el in fnames)