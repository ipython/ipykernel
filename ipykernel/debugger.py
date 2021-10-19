import os
import re

import zmq
from zmq.utils import jsonapi

from tornado.queues import Queue
from tornado.locks import Event

from IPython.core.getipython import get_ipython

try:
    from jupyter_client.jsonutil import json_default
except ImportError:
    from jupyter_client.jsonutil import date_default as json_default

from .compiler import (get_file_name, get_tmp_directory, get_tmp_hash_seed)

# This import is required to have the next ones working...
from debugpy.server import api  # noqa
from _pydevd_bundle import pydevd_frame_utils
from _pydevd_bundle.pydevd_suspended_frames import SuspendedFramesManager, _FramesTracker

# Required for backwards compatiblity
ROUTING_ID = getattr(zmq, 'ROUTING_ID', None) or zmq.IDENTITY


class _FakeCode:
    def __init__(self, co_filename, co_name):
        self.co_filename = co_filename
        self.co_name = co_name


class _FakeFrame:
    def __init__(self, f_code, f_globals, f_locals):
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals
        self.f_back = None


class _DummyPyDB:
    def __init__(self):
        from _pydevd_bundle.pydevd_api import PyDevdAPI
        self.variable_presentation = PyDevdAPI.VariablePresentation()


class VariableExplorer:
    def __init__(self):
        self.suspended_frame_manager = SuspendedFramesManager()
        self.py_db = _DummyPyDB()
        self.tracker = _FramesTracker(self.suspended_frame_manager, self.py_db)
        self.frame = None

    def track(self):
        var = get_ipython().user_ns
        self.frame = _FakeFrame(_FakeCode('<module>', get_file_name('sys._getframe()')), var, var)
        self.tracker.track('thread1', pydevd_frame_utils.create_frames_list_from_frame(self.frame))

    def untrack_all(self):
        self.tracker.untrack_all()

    def get_children_variables(self, variable_ref = None):
        var_ref = variable_ref
        if not var_ref:
            var_ref = id(self.frame)
        variables = self.suspended_frame_manager.get_variable(var_ref)
        return [x.get_var_data() for x in variables.get_children_variables()]


class DebugpyMessageQueue:

    HEADER = 'Content-Length: '
    HEADER_LENGTH = 16
    SEPARATOR = '\r\n\r\n'
    SEPARATOR_LENGTH = 4

    def __init__(self, event_callback, log):
        self.tcp_buffer = ''
        self._reset_tcp_pos()
        self.event_callback = event_callback
        self.message_queue = Queue()
        self.log = log

    def _reset_tcp_pos(self):
        self.header_pos = -1
        self.separator_pos = -1
        self.message_size = 0
        self.message_pos = -1

    def _put_message(self, raw_msg):
        self.log.debug('QUEUE - _put_message:')
        msg = jsonapi.loads(raw_msg)
        if msg['type'] == 'event':
            self.log.debug('QUEUE - received event:')
            self.log.debug(msg)
            self.event_callback(msg)
        else:
            self.log.debug('QUEUE - put message:')
            self.log.debug(msg)
            self.message_queue.put_nowait(msg)

    def put_tcp_frame(self, frame):
        self.tcp_buffer += frame

        self.log.debug('QUEUE - received frame')
        while True:
            # Finds header
            if self.header_pos == -1:
                self.header_pos = self.tcp_buffer.find(DebugpyMessageQueue.HEADER)
            if self.header_pos == -1:
                return

            self.log.debug('QUEUE - found header at pos %i', self.header_pos)

            #Finds separator
            if self.separator_pos == -1:
                hint = self.header_pos + DebugpyMessageQueue.HEADER_LENGTH
                self.separator_pos = self.tcp_buffer.find(DebugpyMessageQueue.SEPARATOR, hint)
            if self.separator_pos == -1:
                return

            self.log.debug('QUEUE - found separator at pos %i', self.separator_pos)

            if self.message_pos == -1:
                size_pos = self.header_pos + DebugpyMessageQueue.HEADER_LENGTH
                self.message_pos = self.separator_pos + DebugpyMessageQueue.SEPARATOR_LENGTH
                self.message_size = int(self.tcp_buffer[size_pos:self.separator_pos])

            self.log.debug('QUEUE - found message at pos %i', self.message_pos)
            self.log.debug('QUEUE - message size is %i', self.message_size)

            if len(self.tcp_buffer) - self.message_pos < self.message_size:
                return

            self._put_message(self.tcp_buffer[self.message_pos:self.message_pos + self.message_size])
            if len(self.tcp_buffer) - self.message_pos == self.message_size:
                self.log.debug('QUEUE - resetting tcp_buffer')
                self.tcp_buffer = ''
                self._reset_tcp_pos()
                return
            else:
                self.tcp_buffer = self.tcp_buffer[self.message_pos + self.message_size:]
                self.log.debug('QUEUE - slicing tcp_buffer: %s', self.tcp_buffer)
                self._reset_tcp_pos()

    async def get_message(self):
        return await self.message_queue.get()


class DebugpyClient:

    def __init__(self, log, debugpy_stream, event_callback):
        self.log = log
        self.debugpy_stream = debugpy_stream
        self.event_callback = event_callback
        self.message_queue = DebugpyMessageQueue(self._forward_event, self.log)
        self.debugpy_host = '127.0.0.1'
        self.debugpy_port = -1
        self.routing_id = None
        self.wait_for_attach = True
        self.init_event = Event()
        self.init_event_seq = -1

    def _get_endpoint(self):
        host, port = self.get_host_port()
        return 'tcp://' + host + ':' + str(port)

    def _forward_event(self, msg):
        if msg['event'] == 'initialized':
            self.init_event.set()
            self.init_event_seq = msg['seq']
        self.event_callback(msg)

    def _send_request(self, msg):
        if self.routing_id is None:
            self.routing_id = self.debugpy_stream.socket.getsockopt(ROUTING_ID)
        content = jsonapi.dumps(
            msg,
            default=json_default,
            ensure_ascii=False,
            allow_nan=False,
        )
        content_length = str(len(content))
        buf = (DebugpyMessageQueue.HEADER + content_length + DebugpyMessageQueue.SEPARATOR).encode('ascii')
        buf += content
        self.log.debug("DEBUGPYCLIENT:")
        self.log.debug(self.routing_id)
        self.log.debug(buf)
        self.debugpy_stream.send_multipart((self.routing_id, buf))

    async def _wait_for_response(self):
        # Since events are never pushed to the message_queue
        # we can safely assume the next message in queue
        # will be an answer to the previous request
        return await self.message_queue.get_message()

    async def _handle_init_sequence(self):
        # 1] Waits for initialized event
        await self.init_event.wait()

        # 2] Sends configurationDone request
        configurationDone = {
            'type': 'request',
            'seq': int(self.init_event_seq) + 1,
            'command': 'configurationDone'
        }
        self._send_request(configurationDone)

        # 3]  Waits for configurationDone response
        await self._wait_for_response()

        # 4] Waits for attachResponse and returns it
        attach_rep = await self._wait_for_response()
        return attach_rep

    def get_host_port(self):
        if self.debugpy_port == -1:
            socket = self.debugpy_stream.socket
            socket.bind_to_random_port('tcp://' + self.debugpy_host)
            self.endpoint = socket.getsockopt(zmq.LAST_ENDPOINT).decode('utf-8')
            socket.unbind(self.endpoint)
            index = self.endpoint.rfind(':')
            self.debugpy_port = self.endpoint[index+1:]
        return self.debugpy_host, self.debugpy_port

    def connect_tcp_socket(self):
        self.debugpy_stream.socket.connect(self._get_endpoint())
        self.routing_id = self.debugpy_stream.socket.getsockopt(ROUTING_ID)

    def disconnect_tcp_socket(self):
        self.debugpy_stream.socket.disconnect(self._get_endpoint())
        self.routing_id = None
        self.init_event = Event()
        self.init_event_seq = -1
        self.wait_for_attach = True

    def receive_dap_frame(self, frame):
        self.message_queue.put_tcp_frame(frame)

    async def send_dap_request(self, msg):
        self._send_request(msg)
        if self.wait_for_attach and msg['command'] == 'attach':
            rep = await self._handle_init_sequence()
            self.wait_for_attach = False
            return rep
        else:
            rep = await self._wait_for_response()
            self.log.debug('DEBUGPYCLIENT - returning:')
            self.log.debug(rep)
            return rep


class Debugger:

    # Requests that requires that the debugger has started
    started_debug_msg_types = [
        'dumpCell', 'setBreakpoints',
        'source', 'stackTrace',
        'variables', 'attach',
        'configurationDone'
    ]

    # Requests that can be handled even if the debugger is not running
    static_debug_msg_types = [
        'debugInfo', 'inspectVariables', 'richInspectVariables'
    ]

    def __init__(self, log, debugpy_stream, event_callback, shell_socket, session):
        self.log = log
        self.debugpy_client = DebugpyClient(log, debugpy_stream, self._handle_event)
        self.shell_socket = shell_socket
        self.session = session
        self.is_started = False
        self.event_callback = event_callback

        self.started_debug_handlers = {}
        for msg_type in Debugger.started_debug_msg_types:
            self.started_debug_handlers[msg_type] = getattr(self, msg_type)

        self.static_debug_handlers = {}
        for msg_type in Debugger.static_debug_msg_types:
            self.static_debug_handlers[msg_type] = getattr(self, msg_type)

        self.breakpoint_list = {}
        self.stopped_threads = []

        self.debugpy_initialized = False

        self.debugpy_host = '127.0.0.1'
        self.debugpy_port = 0
        self.endpoint = None

        self.variable_explorer = VariableExplorer()

    def _handle_event(self, msg):
        if msg['event'] == 'stopped':
            self.stopped_threads.append(msg['body']['threadId'])
        elif msg['event'] == 'continued':
            try:
                self.stopped_threads.remove(msg['body']['threadId'])
            except Exception:
                pass
        self.event_callback(msg)

    async def _forward_message(self, msg):
        return await self.debugpy_client.send_dap_request(msg)

    def _build_variables_response(self, request, variables):
        var_list = [var for var in variables if self.accept_variable(var['name'])]
        reply = {
            'seq': request['seq'],
            'type': 'response',
            'request_seq': request['seq'],
            'success': True,
            'command': request['command'],
            'body': {
                'variables': var_list
            }
        }
        return reply

    @property
    def tcp_client(self):
        return self.debugpy_client

    def start(self):
        if not self.debugpy_initialized:
            tmp_dir = get_tmp_directory()
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            host, port = self.debugpy_client.get_host_port()
            code = 'import debugpy;'
            code += 'debugpy.listen(("' + host + '",' + port + '))'
            content = {
                'code': code,
                'silent': True
            }
            self.session.send(self.shell_socket, 'execute_request', content,
                              None, (self.shell_socket.getsockopt(ROUTING_ID)))

            ident, msg = self.session.recv(self.shell_socket, mode=0)
            self.debugpy_initialized = msg['content']['status'] == 'ok'
        self.debugpy_client.connect_tcp_socket()
        return self.debugpy_initialized

    def stop(self):
        self.debugpy_client.disconnect_tcp_socket()

    async def dumpCell(self, message):
        code = message['arguments']['code']
        file_name = get_file_name(code)

        with open(file_name, 'w') as f:
            f.write(code)

        reply = {
            'type': 'response',
            'request_seq': message['seq'],
            'success': True,
            'command': message['command'],
            'body': {
                'sourcePath': file_name
            }
        }
        return reply

    async def setBreakpoints(self, message):
        source = message["arguments"]["source"]["path"]
        self.breakpoint_list[source] = message["arguments"]["breakpoints"]
        return await self._forward_message(message)

    async def source(self, message):
        reply = {
            'type': 'response',
            'request_seq': message['seq'],
            'command': message['command']
        }
        source_path = message["arguments"]["source"]["path"]
        if os.path.isfile(source_path):
            with open(source_path) as f:
                reply['success'] = True
                reply['body'] = {
                    'content': f.read()
                }
        else:
            reply['success'] = False
            reply['message'] = 'source unavailable'
            reply['body'] = {}

        return reply

    async def stackTrace(self, message):
        reply = await self._forward_message(message)
        # The stackFrames array can have the following content:
        # { frames from the notebook}
        # ...
        # { 'id': xxx, 'name': '<module>', ... } <= this is the first frame of the code from the notebook
        # { frames from ipykernel }
        # ...
        # {'id': yyy, 'name': '<module>', ... } <= this is the first frame of ipykernel code
        # or only the frames from the notebook.
        # We want to remove all the frames from ipykernel when they are present.
        try:
            sf_list = reply["body"]["stackFrames"]
            module_idx = len(sf_list) - next(
                i
                for i, v in enumerate(reversed(sf_list), 1)
                if v["name"] == "<module>" and i != 1
            )
            reply["body"]["stackFrames"] = reply["body"]["stackFrames"][
                : module_idx + 1
            ]
        except StopIteration:
            pass
        return reply

    def accept_variable(self, variable_name):
        forbid_list = [
            '__name__',
            '__doc__',
            '__package__',
            '__loader__',
            '__spec__',
            '__annotations__',
            '__builtins__',
            '__builtin__',
            '__display__',
            'get_ipython',
            'debugpy',
            'exit',
            'quit',
            'In',
            'Out',
            '_oh',
            '_dh',
            '_',
            '__',
            '___'
        ]
        cond = variable_name not in forbid_list
        cond = cond and not bool(re.search(r'^_\d', variable_name))
        cond = cond and variable_name[0:2] != '_i'
        return cond

    async def variables(self, message):
        reply = {}
        if not self.stopped_threads:
            variables = self.variable_explorer.get_children_variables(message['arguments']['variablesReference'])
            return self._build_variables_response(message, variables)
        else:
            reply = await self._forward_message(message)
            # TODO : check start and count arguments work as expected in debugpy
            reply['body']['variables'] = \
                [var for var in reply['body']['variables'] if self.accept_variable(var['name'])]
        return reply

    async def attach(self, message):
        host, port = self.debugpy_client.get_host_port()
        message['arguments']['connect'] = {
            'host': host,
            'port': port
        }
        message['arguments']['logToFile'] = True
        return await self._forward_message(message)

    async def configurationDone(self, message):
        reply = {
            'seq': message['seq'],
            'type': 'response',
            'request_seq': message['seq'],
            'success': True,
            'command': message['command']
        }
        return reply

    async def debugInfo(self, message):
        breakpoint_list = []
        for key, value in self.breakpoint_list.items():
            breakpoint_list.append({
                'source': key,
                'breakpoints': value
            })
        reply = {
            'type': 'response',
            'request_seq': message['seq'],
            'success': True,
            'command': message['command'],
            'body': {
                'isStarted': self.is_started,
                'hashMethod': 'Murmur2',
                'hashSeed': get_tmp_hash_seed(),
                'tmpFilePrefix': get_tmp_directory() + '/',
                'tmpFileSuffix': '.py',
                'breakpoints': breakpoint_list,
                'stoppedThreads': self.stopped_threads,
                'richRendering': True
            }
        }
        return reply

    async def inspectVariables(self, message):
        self.variable_explorer.untrack_all()
        # looks like the implementation of untrack_all in ptvsd
        # destroys objects we nee din track. We have no choice but
        # reinstantiate the object
        self.variable_explorer = VariableExplorer()
        self.variable_explorer.track()
        variables = self.variable_explorer.get_children_variables()
        return self._build_variables_response(message, variables)

    async def richInspectVariables(self, message):
        reply = {
            'type': 'response',
            'sequence_seq': message['seq'],
            'success': False,
            'command': message['command']
        }
        
        var_name = message['arguments']['variableName']
        valid_name = str.isidentifier(var_name)
        if not valid_name:
            reply['body'] = {
                'data': {},
                'metadata': {}
            }
            if var_name == 'special variables' or var_name == 'function variables':
                reply['success'] = True
            return reply

        var_repr_data = var_name + '_repr_data'
        var_repr_metadata = var_name + '_repr_metadata'

        if not self.breakpoint_list:
            # The code did not hit a breakpoint, we use the intepreter
            # to get the rich representation of the variable
            var_repr_data, var_repr_metadata = get_ipython().display_formatter.format(var_name)
        else:
            # The code has stopped on a breakpoint, we use the setExpression
            # request to get the rich representation of the variable
            lvalue = var_repr_data + ',' + var_repr_metadata
            code = 'get_ipython().display_formatter.format(' + var_name+')'
            frame_id = message['arguments']['frameId']
            seq = message['seq']
            request = {
                'type': 'request',
                'command': 'setExpression',
                'seq': seq+1,
                'arguments': {
                    'expression': lvalue,
                    'value': code,
                    'frameId': frame_id
                }
            }
            await self._forward_message(request)

        repr_data = globals()[var_repr_data]
        repr_metadata = globals()[var_repr_metadata]
        body = {
            'data': {},
            'metadata': {}
        }

        for key, value in repr_data.items():
            body['data']['key'] = value
            if key in repr_metadata:
                body['metadata'][key] = repr_metadata[key]

        globals().pop(var_repr_data)
        globals().pop(var_repr_metadata)

        reply['body'] = body
        reply['success'] = True
        return reply

    async def process_request(self, message):
        reply = {}

        if message['command'] == 'initialize':
            if self.is_started:
                self.log.info('The debugger has already started')
            else:
                self.is_started = self.start()
                if self.is_started:
                    self.log.info('The debugger has started')
                else:
                    reply = {
                        'command': 'initialize',
                        'request_seq': message['seq'],
                        'seq': 3,
                        'success': False,
                        'type': 'response'
                    }

        handler = self.static_debug_handlers.get(message['command'], None)
        if handler is not None:
            reply = await handler(message)
        elif self.is_started:
            handler = self.started_debug_handlers.get(message['command'], None)
            if handler is not None:
                reply = await handler(message)
            else:
                reply = await self._forward_message(message)

        if message['command'] == 'disconnect':
            self.stop()
            self.breakpoint_list = {}
            self.stopped_threads = []
            self.is_started = False
            self.log.info('The debugger has stopped')

        return reply
