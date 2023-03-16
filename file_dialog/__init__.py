from sys import platform as _sys_platform
if _sys_platform in ('win32', 'cygwin'):
    from .win import open_file, save_file, choose_dir
elif _sys_platform == 'darwin':
    from .macosx import open_file, save_file, choose_dir
elif _sys_platform[:5] == 'linux':
    from .linux import open_file, save_file, choose_dir

