# Generates multiple clones of the same extension to load on Chrome

import os
import shutil
import base64

encryptedEndsWith = 'SCRIPT-ENCODED'

def encode(message):
    """
    This is just a small level of obfuscation so that we cannot look at our blocklists and see all the time consuming websites we are blocking
    """
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')

def decode(message):
    base64_bytes = base64.b64decode(message)
    return base64_bytes.decode('ascii')

cloneCount = 30

# Script Path
scriptPath = os.path.dirname(os.path.realpath(__file__))

# Extension Name
extensionName = scriptPath.split('/')[-2]

# Src Path
srcPath = os.path.join(scriptPath, '../src')

# Read lists
files = [
    'blockLists/alwaysAllowStartsWithUrl.txt',
    'blockLists/blockAllTabsIfUrlOpen.txt',
    'blockLists/blockedDomains.txt',
    'blockLists/blockedStartsWithUrl.txt',
    'blockLists/regexBlock.txt'
]

# dict of file contents unencrypted
contents = {}

for file in files:
    contents[file] = []
    foundUnencrpytedValue = False

    with open(file, 'r') as fr:
        fileContent = fr.readlines()

    for i, f in enumerate(fileContent):
        if f.endswith('\n'):
            value = f[:-1]
        else:
            value = f

        # "encrypted"
        if value.endswith(encryptedEndsWith):
            # Remove the encrypted indicator
            value = value[:-len(encryptedEndsWith)]
            value = decode(value)

        # not "encrypted"
        else:
            foundUnencrpytedValue = True
            fileContent[i] = encode(f) + encryptedEndsWith + '\n'

        if value.endswith('\n'):
            value = value[:-1]

        contents[file].append(value)

    # write back the values but "encrypted" to the file
    if foundUnencrpytedValue:
        with open(file, 'w') as fr:
            for x in fileContent:
                fr.write(x)

# Create clones, so we can't just disable the single extension
writeUrlContent = ""

text = '{}'.format("','".join(contents[files[0]]))
writeUrlContent += "const alwaysAllowStartsWithUrl = ["
if text:
    writeUrlContent += "'{}'".format(text)
writeUrlContent += "]\n"

text = '{}'.format("','".join(contents[files[1]]))
writeUrlContent += "const blockAllTabsIfUrlOpen = ["
if text:
    writeUrlContent += "'{}'".format(text)
writeUrlContent += "]\n"

text = '{}'.format("','".join(contents[files[2]]))
writeUrlContent += "const blockedDomains = ["
if text:
    writeUrlContent += "'{}'".format(text)
writeUrlContent += "]\n"

text = '{}'.format("','".join(contents[files[3]]))
writeUrlContent += "const blockedStartsWithUrl = ["
if text:
    writeUrlContent += "'{}'".format(text)
writeUrlContent += "]\n"

text = '{}'.format("','".join(contents[files[4]]))
writeUrlContent += "const regexBlock = ["
if text:
    writeUrlContent += "'{}'".format(text)
writeUrlContent += "]\n"

# remove the existing dict folder
distPath = clonePath = os.path.join(scriptPath, "../", "dist")
try:
    shutil.rmtree(distPath)
except:
    pass

os.mkdir(distPath)

for i in range(0, cloneCount):
    clonePath = os.path.join(distPath, "{}-{}-clone".format(extensionName, i))
    shutil.copytree(srcPath, clonePath)

    blockerJsPath = clonePath + '/blocker.js'
    with open(blockerJsPath, 'r') as original: data = original.read()
    with open(blockerJsPath, 'w') as modified: modified.write(writeUrlContent + data)
