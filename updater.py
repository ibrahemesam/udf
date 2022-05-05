import platform
import zipfile
import my; from my import *
import Com; from Com import *
class updater:
  def __init__(self, project_dir, github_repo, def_to_output_progress=emptyDef):
    #note: github_repo is in format of "username/repo_name"
    self.project_dir = project_dir
    self.github_repo = github_repo #releases_repo
    self.def_to_output_progress = def_to_output_progress

  def check_for_updates(self, do_update=True):
    try: current_version = my.version
    except: my.version = current_version = open(self.project_dir+'/version.txt', 'r').read().strip()
    if 'DEV' in current_version: return False #this is the development repo, so do NOT edit it 😒
    if 'nt' in os.name: update_channel = 'win' #if windows => 1.0.3-win-64
    else: update_channel = 'unix' #if unix => 1.0.3-unix-64
    update_channel = f'{update_channel}-{my.get_windows_bit_length()}'
    #print('update_channel') #dbg
    updates_report = unsafe(lambda: requests.get(f'https://raw.githubusercontent.com/{self.github_repo}/main/{update_channel}/updates.report')).text.strip()
    #print('updates_report:', updates_report) #dbg
    if '404: Not Found' in updates_report: return False
    updates_report = eval(updates_report[:1-updates_report.rfind(']')])
    if my.version != updates_report[-1]:
        if do_update: self.update([update_channel, updates_report])
        return [update_channel, updates_report]
    else: return False

  def update(self, updates_info):
    self.def_to_output_progress('Fetching new Version: 0%', 0)
    update_channel, updates_report = updates_info
    def get(_file): return unsafe(lambda: requests.get(f"{self.github_repo}/main/{update_channel}/{_file}")).content
    def get_stream(_file): return unsafe(lambda: requests.get(f"{self.github_repo}/main/{update_channel}/{_file}", stream=True))
    new_version_index = updates_report.index(my.version)+1
    if new_version_index == len(updates_report): exit()
    updates_report = updates_report[new_version_index:]
    #print("updates_report:", updates_report)
    new = []
    abandoned = []
    new_urls = {}
    _each_file_percent = (1/len(updates_report))*20
    for idx, i in enumerate(updates_report): # from old to new
        percent = int(idx*_each_file_percent)
        self.def_to_output_progress(f'Fetching new Version: {percent}%', percent)
        update = get(f"{i}/update.report")
        update = eval(update[:1-update.rfind(']')])
        #if any item in update[0] exists in abandoned: delete it from abandoned
        for n in update[0]:
            if n in abandoned:
                while True:
                    try: abandoned.remove(n)
                    except: break
            #append to new
            new.append(n)
            new_urls[str(n)] = i
        #if any item in update[1] exists in new: delete it from new
        for a in update[1]:
            if a in new:
                while True:
                    try: new.remove(a)
                    except: break
            #append to abandoned
            abandoned.append(a)
    self.def_to_output_progress('Fetching new Version: 24%', 24)
    to_remove_from_abandoned = []
    for a in abandoned:
        if not os.path.exists(self.project_dir+'/'+a[0]):
            to_remove_from_abandoned.append(a)
    self.def_to_output_progress('Fetching new Version: 28%', 28)
    for aa in to_remove_from_abandoned:
        while True:
            try: abandoned.remove(aa)
            except: break
    self.def_to_output_progress('Fetching new Version: 30%', 30)
    abandoned = my.utils.list_pure(abandoned)
    new = my.utils.list_pure(new)
    #print("new:", new)
    #print("abandoned:", abandoned)
    #print("new_urls:-")
    _each_file_percent = (1/len(new))*50
    for idx, n in enumerate(new):
        _str_n = str(n)
        percent = 30+int(idx*_each_file_percent)
        self.def_to_output_progress(f'Getting new Files: {percent}%', percent)
        #print(f"    url of {_str_n}: {new_urls[_str_n]}")
        #download all new with overwrite existing files
        #print(f"{self.github_repo}/{new_urls[_str_n]}/{n[0]}")
        new_file = os.path.join(self.project_dir, n[0])
        os.makedirs("/".join(os.path.split(new_file)[:-1]), exist_ok=True)
        new_file = open(new_file, 'wb')
        response = get_stream(f"/{new_urls[_str_n]}/{n[0]}")
        total_length = response.headers.get('content-length')
        if total_length is None: # no content length header
            new_file.write(response.content)
        else:
            dl = 0; total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                new_file.write(data)
                done = percent+int((dl/total_length)*(_each_file_percent))
                self.def_to_output_progress(f'Getting new Files: {done}%', done)
        new_file.close()
    #delete all abandoned if files exists
    self.def_to_output_progress('Deleting Abandoned Files: 80%', 80)
    for a in abandoned:
        os.remove(self.project_dir+'/'+a[0])
        #todo: delete containing folder if it is empty
    self.def_to_output_progress('Updating Virtual Environment: 85%', 85)
    subprocess.Popen([sys.executable, '-m', 'pip', 'install', '-r', self.project_dir+'/requirements.txt']).wait()
    self.def_to_output_progress('Running post-install Script: 95%', 95)
    if os.path.exists(self.project_dir+'/post-install.py'):
        unsafe(lambda: exec(open(self.project_dir+'/post-install.py').read()))
        os.remove(self.project_dir+'/post-install.py')
    self.def_to_output_progress('The Program is UP-TO-DATE. Restarting...', 100)
    my.psutil.Popen([sys.executable, sys.argv[0]], start_new_session=True)
    sys.exit(0)
    return
    """
    ال abandoned :
    هيتحذف من قايمة ال abandoned: لو في ال new في اصدار احدث منه
    هيتحذف من ال new: لو اصدار الabandoned هو الأحدث
    هيتحذف من الملفات الموجودة بالفعل: لو الملف موجود
    """
