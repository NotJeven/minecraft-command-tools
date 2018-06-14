# minecraft-command-tools
Python scripts to be run console side that assist with Minecraft command (.mcfunction) production.

### Examples
There are a lot of great examples in the ```erisfileparse.py``` file included in the repository.
I mostly left the file manipulation up to the user, as shown in the examples. That means it is required to set up a system for placing a single command into a single array location that is passed to the tools. 

### Example using the msb parse tool
```
"""
takes the MSB file[s] from \raw and updates to minecraft 1.12 standard .mcfunction files in \functions\qc
2018-06-13
"""

import sys, os
sys.path.append(os.path.abspath('c:\\projects\\Minecraft Command Tools'))
from mccommandtools import parsemsb

DIRECTORY_IN = 'c:\\projects\\qc\\raw\\Quarry Carts'
DIRECTORY_OUT = 'c:\\projects\\qc\\dump\\'
print("")
print("# QUARRY CART PARSE TOOL #")
print("from: "+DIRECTORY_IN)
print("to: "+DIRECTORY_OUT)
files = 0		# fun stats keeping thing that does nothing other than flavour console text. This is what I do in 2018.

raw = open(DIRECTORY_IN, "r").readlines()
new_raw = []
for r in raw:
	new_raw.append(r.strip())
name = []
funcs = []
names, funcs = parsemsb(new_raw)

for f in range(len(funcs)-1):
	files +=1
	new_f = open(DIRECTORY_OUT + names[f] + ".mcfunction", "w")
	for c in funcs[f]:
		new_f.write(c+"\n")

print("\nFinished.")
print("Created",files,"files.")
