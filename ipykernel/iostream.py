# coding: utf-8
"""Wrappers for forwarding stdout/stderr over zmq"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
import atexit
import os
import sys
import threading
import uuid
import warnings
from io import StringIO, UnsupportedOperation

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from jupyter_client.session import extract_header

from ipython_genutils import py3compat
from ipython_genutils.py3compat import unicode_type

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

MASTER = 0
CHILD = 1

#-----------------------------------------------------------------------------
# IO classes
#-----------------------------------------------------------------------------

class IOPubThread(object):
    """An object for sending IOPub messages in a background thread
    
    prevents a blocking main thread
    
    IOPubThread(pub_socket).background_socket is a Socket-API-providing object
    whose IO is always run in a thread.
    """

    def __init__(self, socket, pipe=False):
        self.socket = socket
        self.background_socket = BackgroundSocket(self)
        self._master_pid = os.getpid()
        self._pipe_flag = pipe
        self.io_loop = IOLoop()
        if pipe:
            self._setup_pipe_in()
        self.thread = threading.Thread(target=self._thread_main)
        self.thread.daemon = True

    def _thread_main(self):
        """The inner loop that's actually run in a thread"""
        self.io_loop.start()
        self.io_loop.close()

    def _setup_pipe_in(self):
        """setup listening pipe for subprocesses"""
        ctx = self.socket.context

        # use UUID to authenticate pipe messages
        self._pipe_uuid = uuid.uuid4().bytes

        pipe_in = ctx.socket(zmq.PULL)
        pipe_in.linger = 0
        try:
            self._pipe_port = pipe_in.bind_to_random_port("tcp://127.0.0.1")
        except zmq.ZMQError as e:
            warnings.warn("Couldn't bind IOPub Pipe to 127.0.0.1: %s" % e +
                "\nsubprocess output will be unavailable."
            )
            self._pipe_flag = False
            pipe_in.close()
            return
        self._pipe_in = ZMQStream(pipe_in, self.io_loop)
        self._pipe_in.on_recv(self._handle_pipe_msg)
    
    def _handle_pipe_msg(self, msg):
        """handle a pipe message from a subprocess"""
        if not self._pipe_flag or not self._is_master_process():
            return
        if msg[0] != self._pipe_uuid:
            print("Bad pipe message: %s", msg, file=sys.__stderr__)
            return
        self.send_multipart(msg[1:])

    def _setup_pipe_out(self):
        # must be new context after fork
        ctx = zmq.Context()
        pipe_out = ctx.socket(zmq.PUSH)
        pipe_out.linger = 3000 # 3s timeout for pipe_out sends before discarding the message
        pipe_out.connect("tcp://127.0.0.1:%i" % self._pipe_port)
        return ctx, pipe_out

    def _is_master_process(self):
        return os.getpid() == self._master_pid

    def _check_mp_mode(self):
        """check for forks, and switch to zmq pipeline if necessary"""
        if not self._pipe_flag or self._is_master_process():
            return MASTER
        else:
            return CHILD
    
    def start(self):
        """Start the IOPub thread"""
        self.thread.start()
        # make sure we don't prevent process exit
        # I'm not sure why setting daemon=True above isn't enough, but it doesn't appear to be.
        atexit.register(self.stop)
    
    def stop(self):
        """Stop the IOPub thread"""
        if not self.thread.is_alive():
            return
        self.io_loop.add_callback(self.io_loop.stop)
        self.thread.join()
    
    def close(self):
        self.socket.close()
        self.socket = None

    @property
    def closed(self):
        return self.socket is None
    
    def send_multipart(self, *args, **kwargs):
        """send_multipart schedules actual zmq send in my thread.
        
        If my thread isn't running (e.g. forked process), send immediately.
        """

        if self.thread.is_alive():
            self.io_loop.add_callback(lambda : self._really_send(*args, **kwargs))
        else:
            self._really_send(*args, **kwargs)
    
    def _really_send(self, msg, *args, **kwargs):
        """The callback that actually sends messages"""
        mp_mode = self._check_mp_mode()

        if mp_mode != CHILD:
            # we are master, do a regular send
            self.socket.send_multipart(msg, *args, **kwargs)
        else:
            # we are a child, pipe to master
            # new context/socket for every pipe-out
            # since forks don't teardown politely, use ctx.term to ensure send has completed
            ctx, pipe_out = self._setup_pipe_out()
            pipe_out.send_multipart([self._pipe_uuid] + msg, *args, **kwargs)
            pipe_out.close()
            ctx.term()


class BackgroundSocket(object):
    """Wrapper around IOPub thread that provides zmq send[_multipart]"""
    io_thread = None
    
    def __init__(self, io_thread):
        self.io_thread = io_thread
    
    def __getattr__(self, attr):
        """Wrap socket attr access for backward-compatibility"""
        if attr.startswith('__') and attr.endswith('__'):
            # don't wrap magic methods
            super(BackgroundSocket, self).__getattr__(attr)
        if hasattr(self.io_thread.socket, attr):
            warnings.warn("Accessing zmq Socket attribute %s on BackgroundSocket" % attr,
                DeprecationWarning, stacklevel=2)
            return getattr(self.io_thread.socket, attr)
        super(BackgroundSocket, self).__getattr__(attr)
    
    def __setattr__(self, attr, value):
        if attr == 'io_thread' or (attr.startswith('__' and attr.endswith('__'))):
            super(BackgroundSocket, self).__setattr__(attr, value)
        else:
            warnings.warn("Setting zmq Socket attribute %s on BackgroundSocket" % attr,
                DeprecationWarning, stacklevel=2)
            setattr(self.io_thread.socket, attr, value)
    
    def send(self, msg, *args, **kwargs):
        return self.send_multipart([msg], *args, **kwargs)

    def send_multipart(self, *args, **kwargs):
        """Schedule send in IO thread"""
        return self.io_thread.send_multipart(*args, **kwargs)


class OutStream(object):
    """A file like object that publishes the stream to a 0MQ PUB socket.
    
    Output is handed off to an IO Thread
    """

    # The time interval between automatic flushes, in seconds.
    flush_interval = 0.2
    topic=None

    def __init__(self, session, pub_thread, name, pipe=None):
        if pipe is not None:
            warnings.warn("pipe argument to OutStream is deprecated and ignored",
                DeprecationWarning)
        self.encoding = 'UTF-8'
        # This is necessary for compatibility with Python built-in streams
        self.errors = None
        self.session = session
        if not isinstance(pub_thread, IOPubThread):
            # Backward-compat: given socket, not thread. Wrap in a thread.
            warnings.warn("OutStream should be created with IOPubThread, not %r" % pub_thread,
                DeprecationWarning, stacklevel=2)
            pub_thread = IOPubThread(pub_thread)
            pub_thread.start()
        self.pub_thread = pub_thread
        self.name = name
        self.topic = b'stream.' + py3compat.cast_bytes(name)
        self.parent_header = {}
        self._master_pid = os.getpid()
        self._flush_lock = threading.Lock()
        self._flush_timeout = None
        self._io_loop = pub_thread.io_loop
        self._buffer_lock = threading.Lock()
        self._new_buffer()

    def _is_master_process(self):
        return os.getpid() == self._master_pid

    def set_parent(self, parent):
        self.parent_header = extract_header(parent)

    def close(self):
        self.pub_thread = None

    @property
    def closed(self):
        return self.pub_thread is None

    def _schedule_flush(self):
        """schedule a flush in the IO thread
        
        call this on write, to indicate that flush should be called soon.
        """
        with self._flush_lock:
            if self._flush_timeout is not None:
                return
            # None indicates there's no flush scheduled.
            # Use a non-None placeholder to indicate that a flush is scheduled
            # to avoid races while we wait for _schedule_in_thread below to fire in the io thread.
            self._flush_timeout = 'placeholder'
        
        # add_timeout has to be handed to the io thread with add_callback
        def _schedule_in_thread():
            self._flush_timeout = self._io_loop.call_later(self.flush_interval, self._flush)
        self._io_loop.add_callback(_schedule_in_thread)

    def flush(self):
        """trigger actual zmq send
        
        send will happen in the background thread
        """
        if self.pub_thread.thread.is_alive():
            self._io_loop.add_callback(self._flush)
            # wait for flush to actually get through:
            evt = threading.Event()
            self._io_loop.add_callback(evt.set)
            evt.wait()
        else:
            self._flush()
    
    def _flush(self):
        """This is where the actual send happens.
        
        _flush should generally be called in the IO thread,
        unless the thread has been destroyed (e.g. forked subprocess).
        """
        with self._flush_lock:
            self._flush_timeout = None
            data = self._flush_buffer()
        if data:
            # FIXME: this disables Session's fork-safe check,
            # since pub_thread is itself fork-safe.
            # There should be a better way to do this.
            self.session.pid = os.getpid()
            content = {u'name':self.name, u'text':data}
            self.session.send(self.pub_thread, u'stream', content=content,
                parent=self.parent_header, ident=self.topic)
    
    def isatty(self):
        return False

    def __next__(self):
        raise IOError('Read not supported on a write only stream.')

    if not py3compat.PY3:
        next = __next__

    def read(self, size=-1):
        raise IOError('Read not supported on a write only stream.')

    def readline(self, size=-1):
        raise IOError('Read not supported on a write only stream.')

    def fileno(self):
        raise UnsupportedOperation("IOStream has no fileno.")

    def write(self, string):
        if self.pub_thread is None:
            raise ValueError('I/O operation on closed file')
        else:
            # Make sure that we're handling unicode
            if not isinstance(string, unicode_type):
                string = string.decode(self.encoding, 'replace')

            is_child = (not self._is_master_process())
            with self._buffer_lock:
                self._buffer.write(string)
            if is_child:
                # newlines imply flush in subprocesses
                # mp.Pool cannot be trusted to flush promptly (or ever),
                # and this helps.
                if '\n' in string:
                    self.flush()
            else:
                self._schedule_flush()

    def writelines(self, sequence):
        if self.pub_thread is None:
            raise ValueError('I/O operation on closed file')
        else:
            for string in sequence:
                self.write(string)

    def _flush_buffer(self):
        """clear the current buffer and return the current buffer data"""
        with self._buffer_lock:
            data = u''
            if self._buffer is not None:
                buf = self._buffer
                self._new_buffer()
                data = buf.getvalue()
                buf.close()
        return data

    def _new_buffer(self):
        self._buffer = StringIO()
