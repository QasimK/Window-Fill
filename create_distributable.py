"""Call with 'create_exe.py build'"""

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
p = sys.path[:]
p.extend(['src/'])
buildOptions = dict(includes = ['re'], packages = [], excludes = [], path=p)

executables = [
    Executable('src/run_with_console.py', #base='Win32GUI',
               targetName='Window Fill.exe',
               icon='resources/icon.ico')
]


descript = 'Fill the foreground window in the empty space at the mouse cursor.'

setup(name = 'Window Fill',
      version = '1.0',
      description = descript,
      options = dict(build_exe = buildOptions),
      executables = executables)
