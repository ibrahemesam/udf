
def get_free_port(return_socket=False):
    import socket
    for port in range(1025, 65536):  # check for all available ports
        try:
            serv = socket.socket()  # create a new socket
            serv.bind(('0.0.0.0', port))  # bind socket with address
            if return_socket: return serv, port
            serv.close()  # close connection
            return port
        except: continue

def init_remote_debugger(secret="None"):
    import socket, traceback, time
    ## secret is a way of authentication to prevent executing un-authorized code
    # create a socket server with free port
    soc, port = get_free_port(return_socket=True)
    print(f'[DEBUGGER]: running on port {port}') # & secret is: {secret}') 
    # put socket into listening mode  
    soc.listen(5)
    # loop
    while True:
        # Establish connection with client.
        try:
            client, addr = soc.accept() 
        except KeyboardInterrupt:
            return
        # old authentication
        # client_auth = client.recv(4).decode()
        # if client_auth != secret:
        #     # print('client_auth:', client_auth)
        #     client.send('Fuck U'.encode())
        #     client.close()
        #     continue
        # print(client_auth)

        # authentication
        if addr[0] != socket.gethostbyname('localhost'):
            # IDE need Authentication because it executes remote code;
            #     if that code is not authorized, it could be malware!
            client.sendall('Fuck U'.encode())
            client.close()
            continue

        # get python_file_path to execute
        py_file_path = client.recv(1024).decode()
        with open(py_file_path, 'r') as py_file_path:
            code = py_file_path.read()

        # execute the file here and get result if possible
        try:
            try:
                result = str([eval(code)])[1:-1]
            except SyntaxError:
                result = "Null"
                exec(code)
        except:
            result = "[ERROR]\n"+traceback.format_exc()

        # def break_loop(): return
        if f'[break_loop_{port}]' in code:
            client.sendall("Bye bye".encode())
            client.close()
            return
        else:
            # send the result of execution to the client
            client.sendall(result.encode())
            # Close the connection with the client
            client.close()


def py_debug(): # run this py file (arg[0]) in new subprocess || send its path to IDE socket erver
    from subprocess import Popen as po
    import sys, traceback, time, re, os

    py_file_path_with_args = sys.argv[1:]
    try:
        py_file_path = os.path.abspath(py_file_path_with_args[0])
    except IndexError:
        exit(0)
    with open(py_file_path, 'r') as f:
        code = f.read()


    debug_server_info_pattern = re.compile(r'\[DEBUG\]\[port:(.*)\]') #;secret:(.*)\]')
    debug_server_info = debug_server_info_pattern.search(code)
    if debug_server_info:
        # get server port and secret
        server_port = int(debug_server_info.group(1))
        # server_secret = debug_server_info.group(2)
        # init socket client
        import socket            
        s = socket.socket()   
        # connect to server     
        s.connect(('127.0.0.1', server_port))
        # authentication
        # s.sendall(server_secret.encode())
        # send python file path
        s.sendall(py_file_path.encode())
        # recv execution result
        result = s.recv(3500).decode()    
        print("[result]:", result)
        # close connection
        s.close() 
    else:
        # server port and|or server secret does not exist in the py_file; so, execute it normally
        try:
            po(['/home/ibrahem/Desktop/Code/Runtimes/miniconda3/bin/python']+py_file_path_with_args).wait()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    # This must be the launcher script: [ex: py_debug.py __file_to_run__.py]
    py_debug()
