import threading, asyncio, websockets, time, socket, sqlite3




class Server:
    def __init__(self, db_file, port=None, secret='null'):
        self.db_file, self.secret, self.port = db_file, secret, port
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
        # authentication
        # TODO: use better authentication method to eliminate DoS attack
        try: 
            auth = await websocket.recv()
        except:
            self.goodbye(websocket)
            return
        if auth != self.secret:
            try: await websocket.close('fuck you!')
            except: pass
            print('auth:', auth)
            return
            # raise Exception("UnAuthorized client")
        while True:
            try:
                query = await websocket.recv()
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
                            for col in cols: result[col].append(row[col])

                        # encode && send the result
                        result = str(result)
                        await websocket.send(result)

                    # if first item doesn't exist then data is empty
                    else:
                        await websocket.send('null')

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



if __name__ == '__main__':
    Server('tst.db', 3425)

#TODO: make JS interface
#TODO: make PY interface