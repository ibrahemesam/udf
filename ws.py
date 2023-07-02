
import re, struct
from base64 import b64encode
from hashlib import sha1
from socket import error as SocketError
import errno
import threading, asyncio
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
from threading import Thread
import orjson as json
from asyncio import run as asyncio_run
import logging

KEY_REGX = re.compile(b'Sec-WebSocket-Key: (.*)\\r')

FIN    = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT         = 0x1
OPCODE_BINARY       = 0x2
OPCODE_CLOSE_CONN   = 0x8
OPCODE_PING         = 0x9
OPCODE_PONG         = 0xA

CLOSE_STATUS_NORMAL = 1000
DEFAULT_CLOSE_REASON = bytes('', encoding='utf-8')

import traceback

class ThreadWithLoggedException(threading.Thread):
    """
    Similar to Thread but will log exceptions to passed logger.

    Args:
        logger: Logger instance used to log any exception in child thread

    Exception is also reachable via <thread>.exception from the main thread.
    """

    DIVIDER = "*"*80

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = None

    def run(self):
        try:
            if self._target is not None:
                self._target(*self._args, **self._kwargs)
        except:
            print(traceback.format_exc())
        finally:
            del self._target, self._args, self._kwargs


class WebsocketServerThread(ThreadWithLoggedException):
    """Dummy wrapper to make debug messages a bit more readable"""
    pass

class WebsocketServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    daemon_threads = True  # comment to keep threads alive until finished

    def __init__(self, ws_handler, host='127.0.0.1', port=0, threaded=True):
        TCPServer.__init__(self, (host, port), WebSocketHandler)
        self.ws_handler = ws_handler
        self.run_forever(threaded=threaded)
        # self.clients_handlers = []

    def get_port(self):
        return self.socket.getsockname()[1]

    def run_forever(self, threaded):
        try:
            if threaded:
                self.thread = WebsocketServerThread(target=super().serve_forever, daemon=True)
                self.thread.start()
            else:
                super().serve_forever()
        except KeyboardInterrupt:
            self.server_close()
     

    def client_left(self, client_handler):
        print(f"Client({client_handler.client_address}) disconnected")

class recv_thread(threading.Thread):
    def __init__(self, client, handler):
        threading.Thread.__init__(self, daemon=True)
        self.client = client
        self.handler = handler
        self.exit_thread_flag = False
        self.queue = deque()
        self.trigger = threading.Event()
        self.logger = logging.getLogger()
        self.asyncio_loop_set = threading.Event()
        self.start()

    def recv(self, job):
        # print(1)
        self.queue.append(job)
        # print(job)
        self.trigger.set()

    def run(self):
        self.handler.asyncio_loop = self.client.asyncio_loop = self.asyncio_loop = asyncio.new_event_loop()
        self.asyncio_loop_set.set()
        # print(threading.current_thread().ident)
        async def do_job(job):
            try:
                # self.asyncio_loop.run_until_complete(job)
                # print(job[0])
                await job[0](*job[1])
            except Exception as e:
                if "object NoneType can't be used in 'await' expression" in str(e):
                    print(f'ws_clinent method {job[0].__name__} must have async keyword')
                else:
                    print(traceback.format_exc())
        while True:
            self.trigger.wait()
            while self.queue:
                Thread(target=asyncio_run, args=(do_job(self.queue.popleft()),)).start()
            if self.exit_thread_flag:
                return
            self.trigger.clear()
            


    def exit_thread(self):
        self.exit_thread_flag = True
        self.trigger.set()

class WebSocketHandler(StreamRequestHandler):

    def __init__(self, socket, addr, server):
        self._send_lock = threading.Lock()
        # server.clients_handers.append(self)
        self.server = server
        # implement Channels
        self.channels = {
            # "channel_id": {
            # channel: <Channel instance>
            # msgs: [],
            # awaits: null || {
            #     t: <msg.t to be awaited>,
            #     r: <resolve function of the promise>
            # }  
            # }
        }
        # self.asyncio_loop = asyncio.new_event_loop()
        StreamRequestHandler.__init__(self, socket, addr, server)

    def setup(self):
        StreamRequestHandler.setup(self)
        self.keep_alive = True
        self.handshake_done = False
        self.valid_client = False

    def handle(self):
        if not self.handshake_done:
            self.handshake()
        while self.keep_alive:
            self.read_next_message()

    def read_bytes(self, num):
        return self.rfile.read(num)

    def read_next_message(self):
        try:
            b1, b2 = self.read_bytes(2)
        except ConnectionResetError as e:
            if e.errno == errno.ECONNRESET:
                print("Client closed connection.")
                self.keep_alive = 0
                return
            b1, b2 = 0, 0
        except ValueError as e:
            b1, b2 = 0, 0

        # fin    = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if opcode == OPCODE_CLOSE_CONN:
            # print("Client asked to close connection.")
            self.keep_alive = 0
            return
        if not masked:
            # print("Client must always be masked.")
            self.keep_alive = 0
            return

        if opcode == OPCODE_TEXT:
            # opcode_handler = self.client.recv
            pass
        elif opcode == OPCODE_CONTINUATION:
            print("Continuation frames are not supported.")
            return
        elif opcode == OPCODE_BINARY:
            print("Binary frames are not supported.")
            return
        elif opcode == OPCODE_PING:
            print('PING not implemented')
            return
        elif opcode == OPCODE_PONG:
            print('PONG not implemented')
            return
        else:
            print("Unknown opcode %#x." % opcode)
            self.keep_alive = 0
            return

        if payload_length == 126:
            payload_length = struct.unpack(">H", self.rfile.read(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack(">Q", self.rfile.read(8))[0]

        masks = self.read_bytes(4)
        message_bytes = bytearray()
        for message_byte in self.read_bytes(payload_length):
            message_byte ^= masks[len(message_bytes) % 4]
            message_bytes.append(message_byte)
        # opcode_handler(message_bytes)    
        self.recv(message_bytes)
        
    def recv(self, msg):
        # print('server recieved:', msg, self)
        msg = json.loads(msg)
        # print('ol')
        if '_c' in msg: # reserved msg dict items: msg['_c']
            # print(4)
            # print(hasattr(self, 'channels'))
            # print(msg)
            # print(self.channels)
            if msg['_c'] in self.channels:
                # print(8)
                channel = self.channels[msg['_c']]
                channel['msgs'].append(msg)
                # print(9)
                if channel['awaits']: # is not None
                    if msg['t'] == channel['awaits']['t']:
                        # print(3)
                        # self.asyncio_loop.call_soon_threadsafe(channel['awaits']['r'], msg) # continue asynchrous function
                        Thread(target=self.asyncio_loop.call_soon_threadsafe, args=(channel['awaits']['r'], msg)).start() # continue asynchrous function
                        
                        channel['awaits'] = None
                        # print(2)
                        return
                # print(1)
                return # just save msg to queue: channel['msgs']
            # print(channel)
            # print('ok')
            return self.recv_thread.recv((self.client.__getattribute__(msg['t']), (msg,))) # forward to asynchrous function
        # print('oo', self.client.__getattribute__(msg['t']))
        # return self.client.__getattribute__(msg['t'])(msg) # forward to synchrous function
        return Thread(target=self.client.__getattribute__(msg['t']), args=(msg,)).start() # forward to synchrous function

    def send_close(self, status=CLOSE_STATUS_NORMAL, reason=DEFAULT_CLOSE_REASON):
        """
        Send CLOSE to client

        Args:
            status: Status as defined in https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1
            reason: Text with reason of closing the connection
        """
        if status < CLOSE_STATUS_NORMAL or status > 1015:
            raise Exception(f"CLOSE status must be between 1000 and 1015, got {status}")

        header = bytearray()
        payload = struct.pack('!H', status) + reason
        payload_length = len(payload)

        # Send CLOSE with status & reason
        header.append(FIN | OPCODE_CLOSE_CONN)
        header.append(payload_length)
        with self._send_lock:
            self.request.send(header + payload)

    def send(self, message, opcode=OPCODE_TEXT):
        header  = bytearray()
        # try:
        #     payload = json.dumps(message).encode()
        # except AttributeError:
        payload = json.dumps(message)
        payload_length = payload.__len__()

        # Normal payload
        if payload_length <= 125:
            header.append(FIN | opcode)
            header.append(payload_length)

        # Extended payload
        elif payload_length >= 126 and payload_length <= 65535:
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT16)
            header.extend(struct.pack(">H", payload_length))

        # Huge extended payload
        elif payload_length < 18446744073709551616:
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT64)
            header.extend(struct.pack(">Q", payload_length))

        else:
            raise Exception("Message is too big. Consider breaking it into chunks.")

        with self._send_lock:
            self.request.send(header + payload)

    def handshake(self):
        response = b'HTTP/1.1 101 Switching Protocols\r\n'\
                   b'Upgrade: websocket\r\n'              \
                   b'Connection: Upgrade\r\n'             \
                   b'Sec-WebSocket-Accept: %s\r\n'        \
                   b'\r\n' % b64encode(sha1(
                    KEY_REGX.search(self.rfile.read1()).group(1) + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                    ).digest()).strip()

        with self._send_lock:
            self.handshake_done = self.request.send(response)
        self.valid_client = True
        if isinstance(self.server.ws_handler, type):
            client = self.server.ws_handler.__new__(self.server.ws_handler)
        else:
            client = self.server.ws_handler
        client.send = self.send
        client.address = self.client_address
        client.Channel = self.Channel
        client.channels = self.channels
        client.get_channel = self.get_channel
        # print(1)
        self.recv_thread = client.recv_thread = recv_thread(client, self)
        self.recv_thread.asyncio_loop_set.wait()
        # print(hasattr(client, 'recv_thread'))
        # print(client)
        client.__init__()
        self.client = client

    def get_channel(self, cid):
        if cid in self.channels:
            return self.channels[cid]['channel']
        else:
            return self.Channel(cid)

    def Channel(self, *args):
        return Channel(self, *args)
        

    def finish(self):
        if hasattr(self.client, 'onClientClose'):
            self.client.onClientClose()
        # self.server.clients_handers.remove(self)

import time
from collections import deque
class Channel:
    def __init__(self, client_handler, cid=None):
        # client_handler:WebSocketHandler is the handler of the clent's WebSocket
        # cid:Setring is the channel id
        if not cid:
            while True:
                cid = time.time()
                if cid not in client_handler.channels:
                    break
        if isinstance(cid, dict):
            # when msg object is passed instead of just passing msg['_c']
            cid = cid['_c']

        client_handler.channels[cid] = {
            'channel': self,
            'msgs': deque(),
            'awaits': None,
        }
        self.client_handler = client_handler
        self.cid = cid

    def wait4(self, msg_t, check_missed=True):
        future = self.client_handler.asyncio_loop.create_future()
        # check if msg with msg_t has already been recieved
        if check_missed:
            for msg in reversed(self.client_handler.channels[self.cid]['msgs']):
                if msg['t'] == msg_t:
                    future.set_result(msg)
                    return future
        self.client_handler.channels[self.cid]['awaits'] = {
            't': msg_t,
            'r': future.set_result,
        }
        return future

    def get_msgs_before(self, current_msg):
        all_msgs = self.client_handler.channels[self.cid]['msgs']
        msgs_before = []
        while True:
            try:
                msg = all_msgs.popleft()
            except IndexError:
                break
            if msg is not current_msg:
                msgs_before.append(msg)
            else: break
        # for msg in all_msgs:
        #     if msg is not current_msg:
        #         msgs_before.append(msg)
        return msgs_before
        
    def send(self, msg):
        msg['_c'] = self.cid
        self.client_handler.send(msg)
            
    def close(self):
        del self.client_handler.channels[self.cid]

import websocket
class WebsocketClient:
    def __init__(self, url:str, ws_handler, ssl=False, client_pre_exist=False) -> None:
        if not (url.startswith('ws://') or url.startswith('wss://')):
            if ssl:
                url = 'wss://' + url
            else:
                url = 'ws://' + url
        self.ws = websocket.WebSocketApp(url,
            on_open=self.on_open,
            on_message=self.recv,
            on_error=self.on_error,
            on_close=self.onClientClose,) 
               
        if client_pre_exist:
            self.client = ws_handler
            self.channels = ws_handler.channels
            self.recv_thread = ws_handler.recv_thread
            self.asyncio_loop = ws_handler.asyncio_loop
        else:
            if isinstance(ws_handler, type):
                self.client = ws_handler()
            else:
                self.client = ws_handler
            self.channels = {
                # "channel_id": {
                # channel: <Channel instance>
                # msgs: [],
                # awaits: null || {
                #     t: <msg.t to be awaited>,
                #     r: <resolve function of the promise>
                #   }  
                # }
            }
            self.client.channels = self.channels
            self.client.Channel = self.Channel
            self.recv_thread = self.client.recv_thread = recv_thread(self.client, self)

        self.client.continue_job_in_asyncio = self.continue_job_in_asyncio
        self.client.send = self.send
        self.thread = threading.Thread(target=self.ws.run_forever, kwargs={'skip_utf8_validation': True})
        self.thread.start()
    
    def Channel(self, *args):
        return Channel(self, *args)
    
    def close(self):
        self.ws.close()
    
    def continue_job_in_asyncio(self, async_method, msg):
        self.recv_thread.recv((async_method, (msg,)))
    
    def recv(self, ws, message):
        # print('client recieved:', message)
        WebSocketHandler.recv(self, message)

    def on_error(self, ws, error):
        return
        if __debug__:
            print(traceback.format_exc())
            print(error)
            import os
            os._exit(0)
        return
        print(error)

    def onClientClose(self, ws, close_status_code, close_msg):
        if hasattr(self.client, 'onClientClose'):
            self.client.onClientClose()

    def on_open(self, ws):
        return
        print("Opened connection")
        
    def send(self, msg):
        self.ws.send(json.dumps(msg))

    def __del__(self):
        self.ws.close()
        # super().__del__()

if __name__ == '__main__':
    import asyncio
    class Client:
        def __init__(self) -> None:
            print(f"\nNew client connected with address {self.address}")
            self.send({'t': 'welcome', 'v': "Hey, Welcome to the Server !"})
            # c.close()

        # def recv(self, msg):
        #     asyncio.run(self.async_recv(msg))

        # async def async_recv(self, msg):
        #     if len(msg) > 200:
        #         msg = msg[:200]+'..'
        #     print(b"Client said: %s" % msg)
        #     self.send('recieved: '+msg.decode())
            
        async def ping(self, msg):
            print('server: ping recieved on server')
            c = self.Channel(msg)
            print('server: pong sent to client')
            c.send({'t': 'pong'})
            await c.wait4('pong')
            print('server: pong recieved on server')
            c.close()
        
        def onClientClose(self):
            print('TERMINATING')
            import os
            os._exit(0)

    PORT=5555
    server = WebsocketServer(port=PORT, ws_handler=Client)
    print(server.get_port())
    server.run_forever(threaded=True)
    # time.sleep(1)
    class client_ws:
        def welcome(self, msg):
            self.continue_job_in_asyncio(self.ping, msg)

        async def ping(self, msg):
            c = self.Channel()
            print('client: ping sent to server')
            c.send({'t': 'ping'})
            await c.wait4('pong')
            print('client: pong recieved on client')
            print('client: pong sent to server')
            c.send({'t': 'pong'})
            c.close()

    a = WebsocketClient(f'localhost:{PORT}', ws_handler=client_ws)
            
            
    # input()
    input('>> exit ?')

    
