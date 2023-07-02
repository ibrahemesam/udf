import socket
from threading import Thread, Event

BUFFER_END = "🤡".encode('utf-8')

class pyjs(Thread): # Python <==IPC==> NodeJS_Main :: python is the server
    def __init__(self, recv_parser = lambda *a: 0, send_decorator = lambda msg: msg, recv_decorator = lambda msg: msg) -> None:
        super().__init__()
        self.recv_parser = recv_parser
        self.send_decorator = send_decorator
        self.recv_decorator = recv_decorator
        self.socket = socket.socket()
        self.socket.bind(('', 0))
        self.port = self.socket.getsockname()[1]
        self.client_connected = Event()
        self.start()

    def run(self):
        self.socket.listen(5)
        self.client, addr = self.socket.accept()
        self.client_connected.set()
        while True:
            buffer = bytearray()
            while True:
                try:
                    data = self.client.recv(4096)
                except ConnectionResetError: # chient chrome has been terminated
                    return
                if not data:
                    # client has disconnected
                    self.__close_server()
                    return
                buffer.extend(data)
                if data.endswith(BUFFER_END):
                    # print(f'{buffer.decode() = }')
                    # buffer.extend(data.replace(BUFFER_END, b''))
                    for msg in buffer.split(BUFFER_END)[:-1]:
                        self.recv_parser(self.recv_decorator(msg))
                    break
            # print(f'{ buffer = }')
            
            
    def send(self, data):
        self.client_connected.wait()
        try:
            return self.client.send(self.send_decorator(data) + BUFFER_END)
        except OSError:
            print('ipc socket node client has disconnected')
            self.__close_server()
            return -1
            
    def close(self):
        self.__close_client()
        self.__close_server()
        
    def __close_client(self):
        try: self.client.close()
        except: pass
        
    def __close_server(self):
        try: self.socket.shutdown()
        except: pass    

    @staticmethod
    def test():
        from orjson import loads, dumps
        ipc = pyjs(print, dumps, loads)
        print(f'ipc.port = { ipc.port }')
        from time import sleep, time
        while 1:
            sleep(1)
            res = ipc.send(
                {
                    't': 'hi',
                    'v': b'Thank you for connecting ' + str(time()).encode()
                }
            )
            if res == -1:
                break
