"""inprocess OutStream subclass"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from .. import iostream

class OutStream(iostream.OutStream):
    def __init__(self, session, pub_thread, name, pipe=False):
        pub_thread.io_loop = None
        super(OutStream, self).__init__(session, pub_thread, name, pipe=False)
    
    def _schedule_flush(self):
        self.flush()

    def flush(self):
        self._flush()
