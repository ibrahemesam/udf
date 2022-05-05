#this file automatically deploy and zip the program for win64 & win32 & unix64
import os, zipfile
from subprocess import Popen as popen
from py_compile import compile as py_compile
import my; from my import *
#########################################
def get_path(_file):
    #input: /home/ibrahem/mm.cfg
    #output: /home/ibrahem
    _ = os.path.abspath(_file)
    __ = os.path.split(_)[-1]
    return _[:-1-len(__)]
global cp; cp = my.cp
global wine
if os.name == 'nt': wine = []
else: wine = ["/home/ibrahem/Desktop/Code/Runtimes/conty.sh", "wine"]

old_compile = compile
class compile:
    #use default project venv for Linux build
    #convert between wine32 & wine64 for windows build
    compiler = {"win32": "/home/ibrahem/Desktop/Code/Python/wenv-32/python.exe",
                "win64": "/home/ibrahem/Desktop/Code/Python/wenv-64/python.exe"}
    #pys is path of .py files && pycs is the output path of .pyc files
    @staticmethod
    def unix64(pys, pycs):
        for idx, i in enumerate(pys):
            py_compile(os.path.abspath(pys[idx]), os.path.abspath(pycs[idx]))

    @staticmethod
    def win32(pys, pycs):
        code = f"pys = {pys}; pycs = {pycs}; " +\
        "import os; from py_compile import compile as py_compile; " +\
        "[py_compile(os.path.abspath(pys[idx]), os.path.abspath(pycs[idx])) for idx, i in enumerate(pys)]"
        subprocess.Popen(wine + [compile.compiler["win32"], "-c", code], cwd=os.getcwd()).wait()

    @staticmethod
    def win64(pys, pycs):
        code = f"pys = {pys}; pycs = {pycs}; " +\
        "import os; from py_compile import compile as py_compile; " +\
        "[py_compile(os.path.abspath(pys[idx]), os.path.abspath(pycs[idx])) for idx, i in enumerate(pys)]"
        subprocess.Popen(wine + [compile.compiler["win64"], "-c", code], cwd=os.getcwd()).wait()
#########################################
#folders to deploy && build structure
'''
/Legend-Master-win64 |or| ..-win64 |or| ..-unix-32
    +/wenv-64 |or| wenv-32 |or| lvenv-64 => the unZipped python env
    +/win64 |or| win32 |or| unix64
        -.pyc files
        -mm.cfg* (in browser profile)
        -requirements.txt
        -version.txt
        -run_script.py
        -[run.exe] |or| [run(bin) + run.sh]
        /bot_imgs [all]
        /redist [all] + del libpepflashplayer if not linux + add pepflash.dll if windows
        /Data
            /game
                -favicon.ico
                /res
                    background.jpg [:
                /client
                    -crossdomain.xml
                    -index.html
                    -Loading.swf
                    -loar.swf
'''
#########################################
global files
redist = os.listdir('./redist')
redist.remove("libpepflashplayer.so")
for idx, i in enumerate(redist): redist[idx] = ["redist/"+i, "redist"]
general = [
        "requirements.txt", "update-log.txt", "bot_imgs", "Data/game/favicon.ico",
        "Data/game/res/background.jpg", "Data/game/client/crossdomain.xml", "Data/game/client/index.html",
        "Data/game/client/Loading.swf", "Data/game/client/loar.swf", "Data/game/client/hotkeys.min.js",
        "Data/Browser Profile/Pepper Data/Shockwave Flash/System/mms.cfg",
        "Data/Browser Profile/Pepper Data/Shockwave Flash/System/mm.cfg"
        ]
for idx, i in enumerate(general): general[idx] = [i, os.path.split(i)[0]]
files = {
    "pyc": [ #.pyc files
        "Bot_Helper.py", "Bot.py", "Com.py", "crypt.py", "Legend Master.py",
        "my.py", "proxy.py", "syntax.py", "updater.py", "g.py", "auth.py",
        "loading.py", "strbt.py"
        ],
    "general": redist + general, #general for all platforms
    "win32": [ #win32 specific
        ['build/build-assets/run_script.py', ""],
        ['build/build-assets/run/win/run.exe', ""],
        ['build/build-assets/pepflashplayer32_31_0_0_153.dll', 'redist']],
    "win64": [ #win64 specific
        ['build/build-assets/run_script.py', ""],
        ['build/build-assets/run/win/run.exe', ""],
        ['build/build-assets/pepflashplayer64_31_0_0_153.dll', 'redist']],
    "unix64": [ #unix64 specific
        ['build/build-assets/run_script.py', ""],
        ['build/build-assets/run/unix64/run.sh', ""],
        ['redist/libpepflashplayer.so', 'redist']]
    }

global version, old_version, app_name
old_version = None
app_name = "Legend-Master"


def build(_os, version):
    """
    aim: one folder in ./build/Legend-Master-Releases/__PLATFORM__/__VERRSION_NUM__ for win-32 || win-64 || unix-64
    the folder contains only app files for the __PLATFORM__
    it does NOT contain the python runtime
    """

    sw = my.stopWatch(); sw.start()
    print(f'building for {_os}')

    #/build/Legend-Master-Releases/{_os}
    app_dir = f'build/Legend-Master-Releases/{_os}/{version}'
    print('writing folders')
    try: os.mkdir(app_dir)
    except:
        shutil.rmtree(app_dir)
        os.mkdir(app_dir)

    #########/__PLATFORM__########
    print('compiling .py files to .pyc')
    compile_def = eval(f"compile.{_os}")
    pys = files["pyc"]; pycs = []
    for py in pys: pycs.append(f"{app_dir}/{py[:-3]}.pyc")
    compile_def(pys, pycs)

    print("writing files")
    fileWrite(app_dir+'/version.txt', version) #-version.txt
    for i in files['general']+files[_os]: cp(i[0], os.path.join(app_dir, i[1]))
    ##-DONE-##
    print(f'Finished building for {_os} in: {sw.elapsed_time()}'); sw.stop()


def make_update(_os, version, old_version=None):
    #NOTE: this def is: after being happy whith the build ( after confirming it is working properly ): because it deploys the app to the end-user
    #NOTE: how to be happy:-> before this method: copy /build/Legend-Master-Releases/__PLATFORM__/__VERRSION_NUM__ to a tmp test dir && run Legend\ Master.pyc with ~/miniconda3/bin/python3 then check app freatures::: also: do the same for windows using wenv-32 & wenv-64
    """
    aim:-
    -zip all 3 folders in ./build/Legend-Master-Releases/__PLATFORM__/__VERRSION_NUM__ for win-32 win-64 unix-64 && upload them to github as a release
    -modify master version.txt && git commit
    -compare and make update report && git add && git commit && git push
    """
    #########################################
    #               compare.py              #
    #########################################
    if old_version is not None:
        new = f"build/Legend-Master-Releases/{_os}/{version}"
        old = f"build/Legend-Master-Releases/{_os}/{old_version}" #TODO: what if there is no old_version:: if this it the first one ?!
        diff = popen(['diff', '-qr', f'{old}', f'{new}'], stdout=subprocess.PIPE).wait()
        new_files = []; abandoned = []
        for a in diff.stdout.readlines():
            a = a.decode().replace('\n','')
            if a.startswith(f"Only in {new}: "): a = a.replace(f"Only in {new}: ", "")
            elif a.startswith(f"Only in {old}: "):
                a = a.replace(f"Only in {old}: ", "")
                if a.endswith('.report'): continue # ignore .report file
                abandoned.append([a, my.utils.get_sha1(old+"/"+a)])
                continue
            elif a.startswith("Files ") and a.endswith(" differ"):
                a = my.strbt(a, f"Files {old}/", f" and {new}")[0]
            else: continue
            if a.endswith('.report'): continue
            new_files.append([a, my.utils.get_sha1(new+"/"+a)])

        def read(_file): return open(_file).read().strip()
        updates = read(f"build/Legend-Master-Releases/{_os}/updates.report")
        if not updates: updates = []
        else: updates = eval(updates)
        new_version = os.path.split(new)[-1]
        updates.append(new_version)
        open(f"build/Legend-Master-Releases/{_os}/updates.report", 'w').write(str(updates))
        open(f"{new}/update.report", "w").write(str([new_files, abandoned]))
        #print("new:", new_files); print("abandoned:", abandoned)
        """
        [file_name, sha1]
        [[new], [abandoned]]
        ال abandoned بناخد كمان sha1 للملف ، و في الآخر لما بننقل الملفات الجديدة و نحطها في مكانها .. بنشوف: في list ال abandoned لو حاجة فيها موجودة ف الملفات الجديدة : ف بنحذفها من ال abandoned (بنقارن عن طريق ال sha1)، بعد كدا: بنبدأ نحذف ال abandoned لو الملف موجود
        """

        #git: add && commit && pust#
        for idx, i in enumerate(new_files): new_files[idx] = f"{_os}/{version}/{i}"
        popen(['git', 'add']+new_files, cwd='build/Legend-Master-Releases').wait()
        popen(['git', 'commit', '-m', f'commit update report for {_os}-{version}'] , cwd='build/Legend-Master-Releases').wait()
        popen(['git', 'push', '-u', 'origin', 'main'] , cwd='build/Legend-Master-Releases').wait()

    ##deploy latest version zip##
    #prepare update zip#
    print('preparing update')
    app_dir = f'build/Legend-Master-Releases/{_os}/{version}'
    update_zip = f'build/updates/{_os}.zip'
    if os.path.exists(update_zip): os.remove(update_zip)
    zipdir(app_dir, update_zip)
    #upload to github release latest
    print("uploading to github release latest")
    popen(['gh', 'release', 'upload', 'latest', '--clobber', os.path.abspath(update_zip)], cwd='build/Legend-Master-Releases').wait()
    #del update_zip"
    print('cleaning')
    os.remove(update_zip)
    #############


def deploy(version, old_version=None):
    #executes make_update for all 3 oss then update main version.txt#
    #NOTE  read def make_update notes#
    oss = ['win32', 'win64', 'unix64']
    for _os in oss: make_update(_os, version, old_version)
    ##update main version.txt##
    open('build/Legend-Master-Releases/version.txt', 'w').write(version)
    #commit && pust#
    popen(['git', 'commit', '-m', 'update main version.txt'] , cwd='build/Legend-Master-Releases').wait()
    popen(['git', 'push', '-u', 'origin', 'main'] , cwd='build/Legend-Master-Releases').wait()


#TODO Note: work on one-file-downlloader project

if __name__ == "__main__":
    version = '1.0.4'
    sw = my.stopWatch()
    sw.start()
    #build_win(64)
    #build_win(32)
    #build_unix64()
    build("unix64", version)
    make_update("unix64", version)
    print('Finished all in:', sw.elapsed_time())
    sw.stop()
    quit()






