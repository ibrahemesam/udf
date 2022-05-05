
import g
import sys, time, ctypes, os, json, requests, urllib.parse, subprocess, random, datetime, psutil
import textwrap, ctypes, shutil, zipfile, hashlib, traceback, math, threading, webbrowser
from strbt import strbt, isNull
backslash_char = "\\"
class logDb_:
    pass

def dont_run_twice():
    ########## Do Not run app twice in the same time ##########
    g.PID = os.getpid()
    _ = 'pid.txt'
    if os.path.exists(_):
        last_pid = fileRead(_)
        if last_pid != str(g.PID):
            try:
                if psutil.Process(int(last_pid)).cmdline() == psutil.Process(g.PID).cmdline():
                    try: g.gif_process.terminate()
                    except: pass
                    os._exit(0)
            except: pass
        del last_pid
    fileWrite(os.path.abspath(_), str(g.PID))
    del _
    ###########################################################

def get_udf_path(path):
    for _path in sys.path:
        _ = _path+path
        if os.path.exists(_): return _
    print(_,_path)
    raise FileNotFoundError(path)
def sleep_forever():
    while True: time.sleep(999999)
def p(*args, d=None):
    if g.debug['all'] == False: return
    if d:
        if not g.debug[d]: return
    _ = ' '.join([str(a) for a in args])
    print(_)
    if g.debug['log']:
        try: g.ui.exec.emit(lambda: multiLambda(lambda: logDb.execute(f'insert into log values (?, ?)', (_, '')), lambda: logDb.commit()))
        except: pass
    return _
def h(): p("Here")
def t(v): return type(v)

def init_var(value, var_name): globals()[var_name] = value
# todo raise runtime errors on error codes of this file
def jsonRead(file):
    if not os.path.exists(file): raise RuntimeError("Json file does not exist")
    with open(file) as json_file: jsonData = json.load(json_file)
    return jsonData

def jsonWrite(jsonData, file):
    file = file.replace('\\', '/')
    file_path_dir = file[0:file.rfind('/')]
    if not os.path.exists(file_path_dir): os.makedirs(file_path_dir)
    if not os.path.exists(file): open(file, 'a').close()
    with open(file, 'w') as outfile:
        json.dump(jsonData, outfile, ensure_ascii=False, indent=4)

def dictRead(file):
    if not os.path.exists(file): raise RuntimeError("Json file does not exist")
    return eval(open(file).read())

def dictWrite(dict, file):
    file = file.replace('\\', '/')
    if file.startswith("./"): file = file[2:]
    if file.startswith("/"): file = file[1:]
    file_path_dir = file[0:file.rfind('/')] if '/' in file else None
    if file_path_dir == "../" or file_path_dir == "..": file_path_dir = None
    if file_path_dir and not os.path.exists(file_path_dir): os.makedirs(file_path_dir)
    if not os.path.exists(file): open(file, 'a').close()
    open(file, 'w').write(str(dict))

def list_repeated(l): return list(set([x for x in l if l.count(x) > 1])) #repeated_items_of_array

def list_common(list1, list2): return [list(x) for x in set(map(tuple, list1)) & set(map(tuple, list2))]

def repeated_items_of_array(x):
    _size = len(x)
    repeated = []
    for i in range(_size):
        k = i + 1
        for j in range(k, _size):
            if x[i] == x[j] and x[i] not in repeated:
                repeated.append(x[i])
    return repeated

def fileRead(file):
    return open(file).read()

def fileReadBytes(file):
    return open(file, 'rb').read()

def fileWrite(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file2write=open(file_path, 'wb' if type(data) == bytes else 'w')
    file2write.write(data)
    file2write.close()

class stopWatch():
    def __init__(self):
        from timeit import default_timer as timer; self.timer = timer
        from datetime import timedelta; self.timedelta = timedelta
        self.start_time = None
        self.stop_time = None
        self.elapsed_time_before_pause = None
        self.isStopped = False
        self.elapsed_time_before_stop = None
        self.elapsed_ms_before_pause = None

    def start(self):
        if self.start_time != None: raise RuntimeError("You can't start the stopWatch twice. use stopWatch().resume instead !")
        self.start_time = self.timer()

    def elapsed_ms(self):
        if self.start_time == None:
            if not self.isStopped:
                raise RuntimeError("You didn't start the stopWatch. start it first !")
            else:
                return self.elapsed_time_before_stop
                #raise RuntimeError("You have stopped the stopWatch. start it again first !")
        self.end_time = self.timer()
        elapsed_time = (self.end_time - self.start_time)*1000
        if self.elapsed_ms_before_pause != None:
            elapsed_time = self.elapsed_ms_before_pause
        return elapsed_time

    def elapsed_time(self):
        if self.start_time == None:
            if not self.isStopped:
                raise RuntimeError("You didn't start the stopWatch. start it first !")
            else:
                return self.elapsed_time_before_stop
                #raise RuntimeError("You have stopped the stopWatch. start it again first !")
        self.end_time = self.timer()
        elapsed_time = self.timedelta(seconds=self.end_time - self.start_time)
        if self.elapsed_time_before_pause != None:
            elapsed_time = self.elapsed_time_before_pause
        return elapsed_time

    def print_elapsed_time(self):
        print(self.elapsed_time())

    def reset(self):
        self.stop()
        self.start()

    def pause(self):
        if self.start_time == None: raise RuntimeError("You didn't start the stopWatch. start it first !")
        self.end_time = self.timer()
        self.elapsed_time_before_pause = self.timedelta(seconds=self.end_time - self.start_time)
        self.elapsed_ms_before_pause = (self.end_time - self.start_time)*1000

    def resume(self):
        if self.elapsed_time_before_pause == None: raise RuntimeError("You can't resume the stopWatch now. pause it first !")
        self.start_time = self.timer() - self.elapsed_time_before_pause
        self.elapsed_time_before_pause = None

    def stop(self):
        self.elapsed_time_before_stop = self.elapsed_time()
        self.start_time = None
        self.stop_time = None
        self.elapsed_time_before_pause = None
        self.isStopped = True

    def calc_def(self, def_to_execute, returned_time_type=str, get_return_of_def=False):
        self.start()
        return_of_def = def_to_execute()
        self.pause()
        if returned_time_type is str: return [self.elapsed_time(), return_of_def] if get_return_of_def else self.elapsed_time()
        elif returned_time_type is float: return [self.elapsed_ms(), return_of_def] if get_return_of_def else self.elapsed_ms()
        elif returned_time_type is int: return [int(self.elapsed_ms()), return_of_def] if get_return_of_def else int(self.elapsed_ms())

def getIntEquidistantPoints(x1, y1, x2, y2): #gets the int points between two points
    n = int(((((x2 - x1 )**2) + ((y2-y1)**2))**0.5))
    def lerp(v0, v1, i): return v0 + i * (v1 - v0)
    return [(int(x), int(y)) for x,y in [(lerp(x1,x2,1./n*i), lerp(y1,y2,1./n*i)) for i in range(n+1)]]

class thread_task(threading.Thread):
    #todo QThread has an exit method
    #  and for error QThread: Destroyed while thread is still running : https://stackoverflow.com/questions/15702782/qthread-destroyed-while-thread-is-still-running
    def __init__(self, args, onExitArgs=None):
        super(thread_task, self).__init__()
        self.args = args
        self.onExitArgs = onExitArgs

    def run(self):
        global window
        self.exit = False
        try: exec(self.args)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(sys.exc_info()[1])
        if self.onExitArgs != None: self.onExit(self.onExitArgs)

    def onExit(self, args):
        try:exec(args)
        except: p(traceback.format_exc())
    """
    def stop(self):
        self.exit = True
    """

def msleep(ms): time.sleep(ms/1000)

def multiLambda(*lambdas):
    for l in lambdas: l()

def setInterval_thread(exec_lines, interval_ms):
    lines=f"""
while True:
    time.sleep({interval_ms}/1000)
    {exec_lines}
"""
    thread = thread_task(lines)
    thread.start()
    return thread

def get_startup_time():
    import platform
    os_type = platform.system()
    if os_type == "Windows":
        import ctypes
        return ctypes.windll.kernel32.GetTickCount64()
    else:
        import os
        return int(os.popen('uptime -p').read()[:-1].split(' ')[1])*60*1000

def mice(): # returns the mouse cursor position
    import pyautogui
    pos = pyautogui.position()
    return [pos.x, pos.y]

def mice2(x, y):
    import mouse
    mouse.move(x, y) # moves the mouse cursor to (x, y)

def encodeURIComponent(str): return urllib.parse.quote(str, safe='~()*!.\'')

class tempClass: pass
def emptyDef(*args): pass
def get_time(): return datetime.datetime.now().strftime("%d-%m-%Y==%H-%M-%S")

class lambda_thread(threading.Thread):
    #todo QThread has an exit method
    #  and for error QThread: Destroyed while thread is still running : https://stackoverflow.com/questions/15702782/qthread-destroyed-while-thread-is-still-running
    def __init__(self, lambda_code, onExitLambda=None):
        super(lambda_thread, self).__init__()
        self.lambda_code = lambda_code
        self.onExitLambda = onExitLambda
        self.start()
    def run(self):
        self.lambda_code()
        '''try: self.lambda_code()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(sys.exc_info()[1])'''
        if self.onExitLambda:
            try: self.onExitLambda()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(sys.exc_info()[1])

def get_windows_bit_length():
    size = ctypes.sizeof(ctypes.c_voidp)
    if size == 4: return 32
    elif size == 8: return 64
    else: raise Exception("Windows is not 32 or 64. Fuck!")

def copy_class(_class_): return type(f'{_class_.__qualname__}_clone', _class_.__bases__, dict(_class_.__dict__))

def configWrite(name, value):
    if name in [cr[0] for cr in g.db.execute('select name from config')]:
        g.db.execute('UPDATE config SET value = ? WHERE name = ?;', (value, name))
    else:
        g.db.execute(f'insert into config(name, value) values(?, ?)', (name, value))
    g.db.commit();
    g.settings[name] = value

def configRead(name):
    try:
        _ = list(g.db.execute(f'select value from config where name="{name}"'))[0]['value']
        if _ in ['True', 'False', 'None']: return eval(_)
        else: return _
    except: return None

def cp(src, dst, symlinks=False, ignore=None):
    if os.path.isdir(src):
        dst = os.path.join(dst, os.path.basename(os.path.normpath(src)))
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
    else:
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(src, dst)

def zipdir(path, zip_path):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    try: os.remove(zip_path)
    except: pass
    with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as ziph:
        for root, dirs, files in os.walk(path):
            for dir in [dir for dir in dirs if os.listdir(os.path.join(root, dir)) == []]:
                ziph.writestr(os.path.relpath(os.path.join(root, dir), os.path.join(path))+'/', "")
            for file in files:
                with open(os.path.join(root, file), 'rb') as _file:
                    ziph.writestr(os.path.relpath(os.path.join(root, file), os.path.join(path)), _file.read())

def isMainThread():
    return threading.current_thread() is threading.main_thread()

def dictKeyByValue(_dict, _value):
    return list(_dict.keys())[list(_dict.values()).index(_value)]

def _try(code):
    try: return code()
    except: return p(traceback.format_exc())

def dbRead(conn, table, cols, where, one_result=True) -> object:
    if len(cols) >1: one_result = False
    cols = ', '.join([f'"{str(c)}"' for c in cols])
    if where: where = f'where {where}'
    try: cur = conn.execute(f'select {cols} from "{table}" {where}')
    except: return None
    if not one_result: return list(cur)
    _ = list(cur)[0][cols]
    if _ in ['True', 'False', 'None']: return eval(_)
    else: return _

def get_username(): return psutil.Process().username()

def list_pure(l):
    _l = []
    for i in l:
        if i not in _l:
            _l.append(i)
    return _l


def get_sha1(_file_path):
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536 # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()
    with open(_file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data: break
            sha1.update(data)
    return sha1.hexdigest()

def hhmmss(ms):
    # s = 1000
    # m = 60000
    # h = 360000
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, _ = divmod(r, 1000)
    return ("%d:%02d:%02d" % (h,m,s)) if h else ("%d:%02d" % (m,s))

