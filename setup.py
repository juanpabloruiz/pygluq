from distutils.core import setup
from glob import glob
import os

import py2exe

NAME = 'gluqlo'
NAMEPY = NAME+'.py'
NAMEEXE = NAME+'.exe'
NAMESCR = NAME+'.scr'


setup(data_files=[
 ('.',['gluqlo.ttf']+
        glob(r'c:\python27\lib\site-packages\pygame\*.dll')+
	glob(r'C:\WINDOWS\WinSxS\*VC90.CRT*1fc8b3b9a1e18e3b*\*.*')+
	glob(r'C:\WINDOWS\WinSxS\Manifests\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.30729.6161_x-ww_31a54e43.manifest'))
], 
# console=[{'script': NAMEPY}],
 windows=[NAMEPY])

if os.name=='nt':
	# copy as screen-saver
	J=os.path.join
	with open(J('dist', NAMEEXE), 'rb') as f_in:
		with open(J('dist', NAMESCR), 'wb') as f_out:
			f_out.write(f_in.read())