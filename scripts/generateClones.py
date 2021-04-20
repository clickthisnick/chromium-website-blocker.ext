# Generates multiple clones of the same extension to load on Chrome

import os
import shutil
import base64
import os.path
from os import path
from subprocess import call

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
    f"{scriptPath}/../blockLists/alwaysAllowStartsWithUrl.txt",
    f"{scriptPath}/../blockLists/blockAllTabsIfUrlOpen.txt",
    f"{scriptPath}/../blockLists/blockedDomains.txt",
    f"{scriptPath}/../blockLists/blockedStartsWithUrl.txt",
    f"{scriptPath}/../blockLists/regexBlock.txt",
    f"{scriptPath}/../blockLists/blockedRequestInitiator.txt",
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

text = '{}'.format('","'.join(contents[files[5]]))
writeUrlContent += "const blockedRequestInitiator = {"
if text:
    writeUrlContent += '"{}"'.format(text)
writeUrlContent += "}\n"

# remove the existing dict folder
distPath = clonePath = os.path.join(scriptPath, "../", "dist")
try:
    shutil.rmtree(distPath)
except:
    pass

os.mkdir(distPath)

extensionLoadingString = "--load-extension="

for i in range(0, cloneCount):
    clonePath = os.path.join(distPath, "{}-{}-clone".format(extensionName, i))
    shutil.copytree(srcPath, clonePath)

    blockerJsPath = os.path.join(clonePath, 'blocker.js')

    with open(blockerJsPath, 'r') as original: data = original.read()
    with open(blockerJsPath, 'w') as modified: modified.write(writeUrlContent + data)
    extensionLoadingString += f"{clonePath},"

# Remove the final comma
extensionLoadingString = extensionLoadingString[:-1]

# Move the real google chrome to browser
if not path.exists("/Applications/Browser.app"):
    shutil.copyfile('/Applications/Google\ Chrome.app', '/Applications/Browser.app')

bashScript = f"""#!/bin/bash

# Prompt the user to type in something before opening chrome
a=$(osascript -e 'try
tell app "SystemUIServer"
set answer to text returned of (display dialog "What are you going to do?" default answer "")
end
end
activate app (path to frontmost application as text)
answer' | tr '\r' ' ')

# If the dialog box is empty or if you hit cancel then exit

if [[ -z "$a" ]]; then
   exit
elif [[ $a == https://* ]]; then
   homepage=$a
else
   homepage="http://duckduckgo.com/?q=$a"
fi

# Kill any chrome processes
pkill Chrome
pgrep -f mac_popup | xargs kill

/Applications/Browser.app/Contents/MacOS/Google\ Chrome {extensionLoadingString} --dns-prefetch-disable --homepage \"$homepage\" & nohup sh {scriptPath}/mac_popup.sh \"Chrome Goal: $a\" 5 60 &>/dev/null &
"""

chromeInitScript = f"{scriptPath}/../dist/GoogleChrome.sh"

with open(chromeInitScript, 'w') as fr:
    fr.write(bashScript)

rc = call(f"{scriptPath}/appify.sh {chromeInitScript}", shell=True)
