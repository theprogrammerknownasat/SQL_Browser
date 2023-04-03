from cx_Freeze import setup, Executable

build_options = {'packages': [], 'excludes': [], 'include_files': ['images/sql.ico']}

import sys

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('main.py', base=base, icon='images/sql.ico')
]

setup(name='SQL Editor',
      version='1.0',
      description='b',
      options={'build_exe': build_options},
      executables=executables)
