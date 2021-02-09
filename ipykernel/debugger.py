import logging
import os

from zmq.utils import jsonapi
from traitlets import Instance

from asyncio import Queue

class DebugpyMessageQueue:

    HEADER = 'Content Length: '
    HEADER_LENGTH = 16
    SEPARATOR = '\r\n\r\n'
    SEPARATOR_LENGTH = 4

    def __init__(self, event_callback):
        self.tcp_buffer = ''
        self._reset_tcp_pos()
        self.event_callback = event_callback
        self.message_queue = Queue

    def _reset_tcp_pos(self):
        self.header_pos = -1
        self.separator_pos = -1
        self.message_size = 0
        self.message_pos = -1

    def _put_message(self, raw_msg):
        # TODO: forward to iopub if this is an event message
        msg = jsonapi.loads(raw_msg)
        if mes['type'] == 'event':
            self.event_callback(msg)
        else:
            self.message_queue.put_nowait(msg)

    def put_tcp_frame(self, frame):
        self.tcp_buffer += frame
        # TODO: not sure this is required
        #self.tcp_buffer += frame.decode("utf-8")

        # Finds header
        if self.header_pos == -1:
            self.header_pos = self.tcp_buffer.find(DebugpyMessageQueue.HEADER, hint)
        if self.header_pos == -1:
            return
        
        #Finds separator
        if self.separator_pos == -1:
            hint = self.header_pos + DebugpyMessageQueue.HEADER_lenth
            self.separator_pos = self.tcp_buffer.find(DebugpyMessageQueue.SEPARATOR, hint)
        if self.separator_pos == -1:
            return

        if self.message_pos == -1:
            size_pos = self.header_pos + DebugpyMessageQueue.HEADER_lenth
            self.message_pos = self.separator_pos + DebugpyMessageQueue.SEPARATOR_LENGTH
            self.message_size = int(self.tcp_buf[size_pos:self.separator_pos])

        if len(self.tcp_buffer - self.message_pos) < self.message_size:
            return

        self._put_message(self.tcp_buf[self.message_pos:self.message_size])
        if len(self.tcp_buffer - self_message_pos) == self.message_size:
            self.reset_buffer()
        else:
            self.tcp_buffer = self.tcp_buffer[self.message_pos + self.message_size:]
            self._reset_tcp_pos()

    async def get_message(self):
        return await self.message_queue.get()
            

class DebugpyClient:

    def __init__(self, debugpy_socket, debugpy_stream):
        self.debugpy_socket = debugpy_socket
        self.debugpy_stream = debugpy_stream
        self.message_queue = DebugpyMessageQueue(self._forward_event)
        self.wait_for_attach = True
        self.init_event = asyncio.Event()

    def _forward_event(self, msg):
        if msg['event'] == 'initialized':
            self.init_event.set()
        #TODO: send event to iopub

    def _send_request(self, msg):
        content = jsonapi.dumps(msg)
        content_length = len(content)
        buf = DebugpyMessageQueue.HEADER + content_length + DebugpyMessageQueue.SEPARATOR + content_msg
        self.debugpy_socket.send(buf) # TODO: pass routing_id 
    
    async def _wait_for_reponse(self):
        # Since events are never pushed to the message_queue
        # we can safely assume the next message in queue
        # will be an answer to the previous request
        return await self.message_queue.get()

    async def _handle_init_sequence(self):
        # 1] Waits for initialized event
        await self.init_event.wait()
        
        # 2] Sends configurationDone request
        configurationDone = {
            'type': 'request',
            'seq': int(self.init_event_message['seq']) + 1,
            'command': 'configurationDone'
        }
        self._send_request(configurationDone)

        # 3]  Waits for configurationDone response
        await self._wait_for_response()

        # 4] Waits for attachResponse and returns it
        attach_rep = await self._wait_for_response()
        return attach_rep

    async def send_dap_request(self, msg):
        self._send_request(msg)
        if self.wait_for_attach and msg['command'] == 'attach':
            rep = await self._handle_init_sequence()
            self.wait_for_attach = False
            return rep
        else:
            rep = await self._wait_for_reponse()
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
        'debugInfo', 'inspectVariables'
    ]

    log = Instance(logging.Logger, allow_none=True)

    def __init__(self):
        self.is_started = False

        self.header = ''
        
        self.started_debug_handlers = {}
        for msg_type in started_debug_msg_types:
            self.started_debug_handlers[msg_type] = getattr(self, msg_type)

        self.static_debug_handlers = {}
        for msg_type in static_debug_msg_types:
            self.static_debug_handlers[msg_type] = getattr(self, msg_type)

        self.breakpoint_list = {}
        self.stopped_threads = []

    async def _forward_message(self, msg):
        return await self.debugpy_client.send_dap_request(msg)

    def start(self):
        return False

    def stop(self):
        pass

    def dumpCell(self, message):
        return {}

    async def setBreakpoints(self, message):
        source = message['arguments']['source']['path'];
        self.breakpoint_list[source] = message['arguments']['breakpoints']
        return await self._forward_message(message);

    def source(self, message):
        reply = {
            'type': 'response',
            'request_seq': message['seq'],
            'command': message['command']
        }
        source_path = message['arguments']['source']['path'];
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
        reply['body']['stackFrames'] =
            [frame for frame in reply['body']['stackFrames'] if frame['source']['path'] != '<string>']
        return reply

    async def variables(self, message):
        reply = await self._forward_message(message)
        # TODO : check start and count arguments work as expected in debugpy
        return reply

    async def attach(self, message):
        message['arguments']['connect'] = {
            'host': self.debugpy_host,
            'port': self.debugpy_port
        }
        message['arguments']['logToFile'] = True
        return await self._forward_message(message)

    def configurationDone(self, message):
        reply = {
            'seq': message['seq'],
            'type': 'response',
            'request_seq': message['seq'],
            'success': True,
            'command': message['command']
        }
        return reply;

    def debugInfo(self, message):
        reply = {
            'type': 'response',
            'request_seq': message['seq'],
            'success': True,
            'command': message['command'],
            'body': {
                'isStarted': self.is_started,
                'hashMethod': 'Murmur2',
                'hashSeed': 0,
                'tmpFilePrefix': 'coincoin',
                'tmpFileSuffix': '.py',
                'breakpoints': self.breakpoint_list,
                'stoppedThreads': self.stopped_threads
            }
        }
        return reply

    def inspectVariables(self, message):
        return {}

    async def process_request(self, header, message):
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
                        'command', 'initialize',
                        'request_seq', message['seq'],
                        'seq', 3,
                        'success', False,
                        'type', 'response'
                    }

        handler = self.static_debug_handlers.get(message['command'], None)
        if handler is not None:
            reply = await handler(message)
        elif self.is_started:
            self.header = header
            handler = self.started_debug_handlers.get(message['command'], None)
            if handler is not None:
                reply = await handler(message)
            else
                reply = await self._forward_message(message)

        if message['command'] == 'disconnect':
            self.stop()
            self.breakpoint_list = {}
            self.stopped_threads = []
            self.is_started = False
            self.log.info('The debugger has stopped')

        return reply

