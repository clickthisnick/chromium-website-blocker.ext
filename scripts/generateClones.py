# Generates multiple clones of the same extension to load on Chrome

import os
import shutil
import base64
import os.path
from os import path
from subprocess import call
import string
import random

encryptedEndsWith = "SCRIPT-ENCODED"


def encode(message):
    """
    This is just a small level of obfuscation so that we cannot look at our blocklists and see all the time consuming websites we are blocking
    """
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode("ascii")


def decode(message):
    base64_bytes = base64.b64decode(message)
    return base64_bytes.decode("ascii")


def generateBlockCode():
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

        with open(file, "r") as fr:
            fileContent = fr.readlines()

        for i, f in enumerate(fileContent):
            if f.endswith("\n"):
                value = f[:-1]
            else:
                value = f

            # "encrypted"
            if value.endswith(encryptedEndsWith):
                # Remove the encrypted indicator
                value = value[: -len(encryptedEndsWith)]
                value = decode(value)

            # not "encrypted"
            else:
                foundUnencrpytedValue = True
                fileContent[i] = encode(f) + encryptedEndsWith + "\n"

            if value.endswith("\n"):
                value = value[:-1]

            contents[file].append(value)

        # write back the values but "encrypted" to the file
        if foundUnencrpytedValue:
            with open(file, "w") as fr:
                for x in fileContent:
                    fr.write(x)

    # Create clones, so we can't just disable the single extension
    writeUrlContent = ""

    text = "{}".format("','".join(contents[files[0]]))
    writeUrlContent += "const alwaysAllowStartsWithUrl = ["
    if text:
        writeUrlContent += "'{}'".format(text)
    writeUrlContent += "]\n"

    text = "{}".format("','".join(contents[files[1]]))
    writeUrlContent += "const blockAllTabsIfUrlOpen = ["
    if text:
        writeUrlContent += "'{}'".format(text)
    writeUrlContent += "]\n"

    text = "{}".format("','".join(contents[files[2]]))
    writeUrlContent += "const blockedDomains = ["
    if text:
        writeUrlContent += "'{}'".format(text)
    writeUrlContent += "]\n"

    text = "{}".format("','".join(contents[files[3]]))
    writeUrlContent += "const blockedStartsWithUrl = ["
    if text:
        writeUrlContent += "'{}'".format(text)
    writeUrlContent += "]\n"

    text = "{}".format("','".join(contents[files[4]]))
    writeUrlContent += "const regexBlock = ["
    if text:
        writeUrlContent += "'{}'".format(text)
    writeUrlContent += "]\n"

    text = "{}".format('","'.join(contents[files[5]]))
    writeUrlContent += "const blockedRequestInitiator = {"
    if text:
        writeUrlContent += '"{}"'.format(text)
    writeUrlContent += "}\n"

    return writeUrlContent


def generateAllClones(distPath):
    cloneCount = 30

    # remove the existing dict folder
    try:
        shutil.rmtree(distPath)
    except:
        pass

    os.mkdir(distPath)

    extensionLoadingString = ""
    letters = string.ascii_letters

    for i in range(0, cloneCount):
        clonePath = os.path.join(
            distPath,
            "extensions",
            "{}-{}-clone".format(
                extensionName + "".join(random.choice(letters) for i in range(21)), i
            ),
        )
        shutil.copytree(srcPath, clonePath)

        blockerJsPath = os.path.join(clonePath, "blocker.js")

        with open(blockerJsPath, "r") as original:
            data = original.read()
        with open(blockerJsPath, "w") as modified:
            modified.write(writeUrlContent + data)
        extensionLoadingString += f"{clonePath},"

    # Remove the final comma
    extensionLoadingString = extensionLoadingString[:-1]


# Script Path
scriptPath = os.path.dirname(os.path.realpath(__file__))
distPath = clonePath = os.path.join(scriptPath, "../", "dist")
extPath = clonePath = os.path.join(distPath, "extensions")

# Extension Name
extensionName = scriptPath.split("/")[-2]

# Src Path
srcPath = os.path.join(scriptPath, "../src")

# Generate block code
writeUrlContent = generateBlockCode()

generateAllClones(distPath)

# Prompt the user to type in something before opening chrome
# a=$(osascript -e 'try
# tell app "SystemUIServer"
# set answer to text returned of (display dialog "What are you going to do?" default answer "")
# end
# end
# activate app (path to frontmost application as text)
# answer' | tr '
#' ' ')
# randomFile=$(ls /Applications/*.app/Contents/MacOS/Google\ Chrome*)
# myarray=$(echo $randomFile | tr '/' ' ')
# IFS=' '
# stringarray=($myarray)
# randomNameWithApp=${{stringarray[1]}}


# Move the real google chrome to browser, makes it easier to mv and then there is no confusion between googlechrome vs google chrome
if path.exists("/Applications/Google Chrome.app"):
    shutil.move("/Applications/Google Chrome.app", "/Applications/Browser.app")

# You can tack this on the the chrome opening, but sometimes it will crash websites
# & nohup sh /Users/mycomputer/dev/chromium-website-blocker.ext/scripts/mac_popup.sh "Chrome Goal: $a" 5 60 &>/dev/null &

bashScript = f"""#!/bin/bash

# Disable incognito mode which extensions have to be explicitly installed and allowed
# ie. Enabling extensions via cli won't work in incognito mode
# 1 disables
defaults write com.google.chrome IncognitoModeAvailability -integer 1

# Disable guest mode which wouldn't have extensions installed
defaults write com.google.Chrome BrowserGuestModeEnabled -bool false

# Don't allow anyone to add guests which then wouldn't have the extensions installed
defaults write com.google.Chrome BrowserAddPersonEnabled -bool false

# If the dialog box is empty or if you hit cancel then exit
homepage="http://duckduckgo.com"

# Kill any chrome processes
pkill Chrome
pgrep -f mac_popup | xargs kill

# Get the location of the real chrome app
newRandomName=$(xxd -l 32 -c 32 -p < /dev/random)
chromeAppLocation=$(ls /Applications/*.app/Contents/MacOS/Google\ Chrome*)
IFS='/'
read -a strarr <<< "$chromeAppLocation"
realChromeRandomDirName=${{strarr[2]}}
IFS=' '
mv /Applications/${{realChromeRandomDirName}} /Applications/${{newRandomName}}.app

# Rename all folders with a prefix
find {extPath} -maxdepth 1 -mindepth 1 -type d -execdir bash -c 'mv "$1" "./a${{1#./}}"' mover {{}} \;

extensionsCommaDelimited=$(ls -d {extPath}/* | grep clone | tr '\n' ',')

/Applications/${{newRandomName}}.app/Contents/MacOS/Google\ Chrome --load-extension=${{extensionsCommaDelimited}} --no-default-browser-check --dns-prefetch-disable --homepage "$homepage"
"""

# Remove GoogleChrome in this dir
custom_chrome_dist_path = f"{scriptPath}/../GoogleChrome.app"
os.system(f"rm -rf {custom_chrome_dist_path}")

chromeInitScript = f"{distPath}/GoogleChrome.sh"

with open(chromeInitScript, "w") as fr:
    fr.write(bashScript)

rc = call(f"{scriptPath}/appify.sh {chromeInitScript}", shell=True)

# Remove any existing GoogleChrome custom app and move our newly generated one to that path
application_chrome_path = "/Applications/GoogleChrome.app"
os.system(f"rm -rf {application_chrome_path}")
os.system(f"mv {custom_chrome_dist_path} {application_chrome_path}")
