
import threading, asyncio, websockets, time, socket, os, uuid, sys, random
import orjson as json
from collections import deque

class start_new_thread(threading.Thread):
    def __init__(self, _lambda, *args, **kwargs):
        super().__init__()
        self._lambda = _lambda
        self.args = args
        self.kwargs = kwargs
        self.start()

    def run(self):
        self._lambda(*self.args, **self.kwargs)

def emptyDef(*args, **kwargs): pass

class client:
    clients = []
    # on_new_ws = emptyDef
    def __init__(self, ws, path):
        # print(f'new ws connection: {ws}')
        client.clients.append(self)
        self.cdex = len(client.clients)-1 #self.client_index
        self.ws = ws
        self.ws_promises_resolve = {}

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
        class Channel:
            def __init__(_self, cid=None):
                # cid:Setring is the channel id
                if not cid:
                    while True:
                        cid = time.time()
                        if cid not in self.channels:
                            break

                self.channels[cid] = {
                    'channel': _self,
                    'msgs': deque(),
                    'awaits': None,
                }
                _self.cid = cid

            def wait4(_self, msg_t):
                future = self.asyncio_loop.create_future()
                self.channels[_self.cid]['awaits'] = {
                    't': msg_t,
                    'r': future.set_result,
                }
                return future

            def get_msgs_before(_self, current_msg):
                all_msgs = self.channels[_self.cid]['msgs']
                msgs_before = []
                while True:
                    msg = all_msgs.popleft()
                    if msg is not current_msg:
                        msgs_before.append(msg)
                    else: break
                # for msg in all_msgs:
                #     if msg is not current_msg:
                #         msgs_before.append(msg)
                return msgs_before
                
            def send(_self, msg):
                msg['_c'] = _self.cid
                self.send(msg)
                    
            def close(_self):
                del self.channels[_self.cid]

        self.Channel = Channel
        self.init_child_class()

    def get_channel(self, cid):
        if cid in self.channels:
            return self.channels[cid]['channel']
        else:
            return self.Channel(cid)

    def init_child_class(self):
        self.client = client.child_class.__new__(client.child_class)
        self.client.send = self.send
        self.client.ws_promises_resolve = self.ws_promises_resolve
        self.client.send_await = self.send_await
        self.client.create_cid = self.create_cid
        self.client.remove_cid = self.remove_cid
        self.client.channels = self.channels
        self.client.Channel = self.Channel
        self.client.ws = self.ws
        self.client.__init__()

    async def recv(self, msg):
        try: await self.client.recv(msg)
        except Exception as e:
            if str(e) == "'client' object has no attribute 'recv'": pass
            else: raise e

    async def _recv(self):
        websocket = self.ws
        while True:
            try: msg = await websocket.recv()
            except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError) as e:
                self.onClientClose(e)
                return
            except OSError as e:
                if "Transport endpoint is not connected" in str(e):
                    self.onClientClose(e)
                    return
            asyncio.create_task(self.recv(msg))

    def send(self, msg):
        asyncio.run_coroutine_threadsafe(self._send(msg), loop=client.asyncio_loop)

    async def _send(_client, msg):
        try: await _client.ws.send(json.dumps(msg))
        except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError) as e:
            _client.onClientClose(e)
            return

    def create_cid (self):
        # cid:Setring is the channel id
        while True:
            cid = str(time.time()) + str(random.random())
            if cid not in self.ws_promises_resolve:
                return cid

    def remove_cid(self, cid):
        if cid in self.ws_promises_resolve:
            del self.ws_promises_resolve[cid]

    def send_await(self, msg, cid=None):
        # USAGE: print((await self.send_await({ t: "ping" })).t);
        if type(msg) !=  dict:
            print("msg must be JSON object, so that this method can work efficiently")
            msg = json.loads(msg)
        if cid:
            # init the channel msg
            msg['jp'] = msg['pp'] = cid
        else:
            msg['pp'] = self.create_cid() # pp: Python Promise

        future = self.asyncio_loop.create_future()
        self.ws_promises_resolve[msg['pp']] = future.set_result
        self.send(msg)
        return future

    def onClientClose(self, exception):
        try: client.clients.remove(self)
        except ValueError: pass
        try: self.client.onClientClose(exception)
        except Exception as e:
            if str(e) == "'client' object has no attribute 'onClientClose'": pass
            else: raise e

async def ws_hellow(websocket, path):
    await client(websocket, path)._recv()

def init_server(on_port=emptyDef, child_class=None, new_thread=True):
    # on_port is a def that recieves port as first parameter
    if child_class: client.child_class = child_class
    async def run_server():
        client.asyncio_loop = asyncio.get_running_loop()
        async with websockets.serve(ws_hellow, "0.0.0.0") as server:
            on_port(server.sockets[0].getsockname()[1])
            await asyncio.Future()  # run forever
    
    # asyncio.ensure_future(run_server())
    # asyncio.main_loop = asyncio.get_event_loop()
    
    if new_thread:
        thread = start_new_thread(asyncio.run, run_server())
        return thread
    else:
        asyncio.run(run_server())

def get_free_port(exclude=[], reflect=False):
    _ = range(1025, 65535)
    if reflect: _ = _[::-1]
    for port in _:  # check for all available ports
        try:
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a new socket
            serv.bind(('0.0.0.0', port))  # bind socket with address
            serv.close()  # close connection
            if port in exclude: continue
            #my.p('free port', port)
            return port
        except: continue
if __name__ == '__main__':
    # TODO: make a USAGE example
    class ws_client: # Just a template to copy-paste when using this ws.py module
        clients = {}
        def __init__(self):
            self.code = str(uuid.uuid4())
            ws_client.clients[self.code] = self

        async def recv(self, msg):
            # NOTE: this method must be async, you don't have to use await here, but leave async keyword as is
            msg = eval(msg)
            if 'pp' in msg:
                # if 'pp' in msg.keys()      so, this msg is a resolve of a python promise [ie: send_await]
                self.ws_promises_resolve[msg['pp']](msg)
                del self.ws_promises_resolve[msg['pp']]
                return
            # match msg["t"]: # msg["type"]
            #     case 'welcome':
            #         print('welcome:', self.code)

        def onClientClose(self, exception):
            del ws_client.clients[self.code]
            if 'received 1001 (going away); then sent 1001 (going away)' in str(exception):
                print(f'Client [{self.code}] went away.')
