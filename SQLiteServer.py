import threading, asyncio, websockets, time, socket, sqlite3

class Server:
    def __init__(self, db_file, port=None, secret='null', pong="SQLiteServer"):
        if secret == 'ping': raise Exception('secret can NOT be "ping"')
        self.db_file, self.secret, self.port, self.pong = db_file, secret, port, pong
        threading.Thread(target=self.start, args=()).start()

    def start(self):
        self.db = sqlite3.connect(self.db_file)
        self.db.row_factory = sqlite3.Row
        async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(async_loop)
        server = websockets.serve(self.ws_hellow, "127.0.0.1", self.port)
        asyncio.ensure_future(server)
        async_loop.run_forever()

    async def ws_hellow(self, websocket, path):
        try: 
            first_msg = await websocket.recv()
        except:
            self.goodbye(websocket)
            return
        # if first_msg is ping, then pong
        if first_msg == 'ping':
            await websocket.send(self.pong)
            return
        else: auth = first_msg
        # authentication
        # TODO [Security]: use better authentication method to eliminate DoS attack
        if auth != self.secret:
            await websocket.send('fuck you!')
            print('auth_failed:', auth)
            return
            # raise Exception("UnAuthorized client")
        while True:
            try:
                msg = await websocket.recv()
                # if query is ping, then pong
                if msg == 'ping':
                    await websocket.send(self.pong)
                    continue
                else: query = msg
                # print('query:', query)
                try:
                    # execute query
                    cursor = self.db.execute(query)
                    first_row = cursor.fetchone()
                    if first_row:
                        # parse returned data
                        cols = first_row.keys() # get columns

                        # add first_row && make result structure
                        result = {}
                        # {
                        # "col1": ['A', 'B', 'C'],
                        # "col2": ['D', 'E', 'F'],
                        # }
                        for col in cols: result[col] = [first_row[col]]

                        # add the rest of rows
                        for row in cursor:
                            row = tuple(row)
                            for idx, col in enumerate(cols): result[col].append(row[idx])

                        # encode && send the result
                        result = str(result)
                        await websocket.send(result)

                    # if first item doesn't exist then data is empty
                    else:
                        await websocket.send('None')

                    cursor.close() # close the cursor
                except Exception as e:
                    #if there is any error
                    await websocket.send(f'[Error]: {e}')
                    continue
                # commit changes
                self.db.commit()


            except Exception as e:
                self.goodbye(websocket, e)
                return
                
    def goodbye(self, websocket, exception=None):
        if exception: print(exception)
        print('goodbye <3')
        return

    class connect:
        ###
        # client reqires: pip install websocket-client
        ###
        def __init__(self, ip, port, secret):
            from websocket import create_connection
            self.ws = create_connection(f"ws://{ip}:{port}")
            # authentication
            self.ws.send(secret)
            # keep alive
            self.keep_alive()

        def query(self, query):
            self.ws.send(query)
            data = self.ws.recv()
            if data.startswith('[Error]:'):
                raise Exception(data)
            return eval(data)

        def close(self): self.ws.close()

        def keep_alive(self):
            # workaround for this error:
            #     sent 1011 (unexpected error) keepalive ping timeout; no close frame received
            import time
            async def _keepalive():
                while True:
                    time.sleep(15)
                    self.ws.send('ping')
                    self.ws.recv() # recv pong
            threading.Thread(
                target=(lambda: asyncio.new_event_loop()\
                    .run_until_complete(_keepalive()))
                    , args=()).start()
            

if __name__ == '__main__':
    Server('tst.db', 3425)
    import time
    time.sleep(1)
    sql = Server.connect('127.0.0.1', 3425, 'null')
    print(sql.query('select * from users'))
    while 1:
        i = input('>>> ')
        if i == 'q': break
        try:
            print(sql.query(i))
        except Exception as e:
            print(e)

