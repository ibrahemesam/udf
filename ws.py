
import threading, asyncio, websockets, time, socket

class start_new_thread(threading.Thread):
    def __init__(self, _lambda):
        super().__init__()
        self._lambda = _lambda
        self.start()

    def run(self):
        self._lambda()

def emptyDef(*args, **kwargs): pass

class client:
    clients = []
    on_new_ws = emptyDef
    def __init__(self, ws):
        #print(f'new ws connection: {ws}')
        client.clients.append(self)
        self.cdex = len(client.clients)-1 #self.client_index
        self.ws = ws
        self.asyncloop_send = asyncio.new_event_loop()
        self.send_lock = threading.Lock()
        # start_new_thread(self.asyncloop_send.run_forever)
        self.client = client.child_class()
        self.client.send = self.send
        self.client.ws = ws

    def recv(self, msg):
        try: self.client.recv(msg)
        except Exception as e:
            if str(e) == "'client' object has no attribute 'recv'": pass
            else: raise e

    def send(self, msg):
        #FIXME: wait for eventloop to finish
        """
Exception in thread Thread-15:
Traceback (most recent call last):
  File "/home/ibrahem/miniconda3/lib/python3.9/threading.py", line 954, in _bootstrap_inner
    self.run()
  File "/home/ibrahem/mnt/Files/Desktop/Code/Projects/Family-Pharma/rx/ws.py", line 11, in run
    self._lambda()
  File "/home/ibrahem/mnt/Files/Desktop/Code/Projects/Family-Pharma/rx/ws.py", line 38, in <lambda>
    start_new_thread(lambda: self.asyncloop_send.run_until_complete(send(self, msg)))
  File "/home/ibrahem/miniconda3/lib/python3.9/asyncio/base_events.py", line 618, in run_until_complete
    self._check_running()
  File "/home/ibrahem/miniconda3/lib/python3.9/asyncio/base_events.py", line 578, in _check_running
    raise RuntimeError('This event loop is already running')
RuntimeError: This event loop is already running
/home/ibrahem/miniconda3/lib/python3.9/threading.py:956: RuntimeWarning: coroutine 'send' was never awaited
  self._invoke_excepthook(self)
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
Client [admin] went away
Exception in thread Thread-17:
Traceback (most recent call last):
  File "/home/ibrahem/miniconda3/lib/python3.9/threading.py", line 954, in _bootstrap_inner
    self.run()
  File "/home/ibrahem/mnt/Files/Desktop/Code/Projects/Family-Pharma/rx/ws.py", line 11, in run
    self._lambda()
  File "/home/ibrahem/mnt/Files/Desktop/Code/Projects/Family-Pharma/rx/ws.py", line 38, in <lambda>
    start_new_thread(lambda: self.asyncloop_send.run_until_complete(send(self, msg)))
  File "/home/ibrahem/miniconda3/lib/python3.9/asyncio/base_events.py", line 618, in run_until_complete
    self._check_running()
  File "/home/ibrahem/miniconda3/lib/python3.9/asyncio/base_events.py", line 578, in _check_running
    raise RuntimeError('This event loop is already running')
RuntimeError: This event loop is already running
        """
        # start_new_thread(lambda: self.asyncloop_send.run_until_complete(send(self, msg)))
        self.send_lock.acquire(True)
        start_new_thread(lambda: self._send(msg))
        self.send_lock.release()


    def _send(self, msg):
        self.send_lock.acquire(True)
        self.asyncloop_send.run_until_complete(send(self, msg))
        time.sleep(0.1)
        self.send_lock.release()

    def onClientClose(self, exception):
        client.clients.remove(self)
        try: self.client.onClientClose(exception)
        except Exception as e:
            if str(e) == "'client' object has no attribute 'onClientClose'": pass
            else: raise e

async def send(_client, msg):
    try: await _client.ws.send(msg)
    except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError) as e:
        _client.onClientClose(e)
        return

async def recv(_client):
    websocket = _client.ws
    while True:
        try: _client.recv(await websocket.recv()) #asyncio.wait(3)
        except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError) as e:
            _client.onClientClose(e)
            return
        except OSError as e:
          if "Transport endpoint is not connected" in str(e):
            _client.onClientClose(e)
            return

async def ws_hellow(websocket, path):
    _client = client(websocket)
    await recv(_client)

def init_server(port=5678, child_class=None):
    server = websockets.serve(ws_hellow, "127.0.0.1", port)
    asyncio.ensure_future(server)
    asyncio.main_loop = asyncio.get_event_loop()
    if child_class: client.child_class = child_class
    start_new_thread(asyncio.main_loop.run_forever)
    return server

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


