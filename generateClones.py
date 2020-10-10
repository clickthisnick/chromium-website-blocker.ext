# Generates multiple clones of the same extension to load on Chrome

import os
import shutil

cloneCount = 30

# Script Path
scriptPath = os.path.dirname(os.path.realpath(__file__))

# Extension Name
extensionName = scriptPath.split('/')[-1]

# Src Path
srcPath = os.path.join(scriptPath, 'src')

allDirectories = os.listdir(scriptPath)

# Remove old clone extensions
for x in allDirectories:
    if x.endswith('clone'):
        shutil.rmtree(x)

# Create clones, so we can't just disable the single extension
for i in range(0, cloneCount):
    clonePath = os.path.join(scriptPath, "{}-{}-clone".format(extensionName, i))
    shutil.copytree(srcPath, clonePath)
