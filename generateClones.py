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

# Read lists
# Urls to never block even tho the domain itself might be blocked
# Can be a full url like https://an.example.com
with open('blockLists/alwaysAllowStartsWithUrl.txt', 'r') as fr:
    alwaysAllowStartsWithUrl = fr.readlines()
    alwaysAllowStartsWithUrl = [f.split('\n')[0] for f in alwaysAllowStartsWithUrl]

with open('blockLists/blockAllTabsIfUrlOpen.txt', 'r') as fr:
    blockAllTabsIfUrlOpen = fr.readlines()
    blockAllTabsIfUrlOpen = [f.split('\n')[0] for f in blockAllTabsIfUrlOpen]

# List of domains to block
# Must be just the domain (example.com not an.example.com)
# You will need to allow specific subdomains or queries within a blocked domain
with open('blockLists/blockedDomains.txt', 'r') as fr:
    blockedDomains = fr.readlines()
    blockedDomains = [f.split('\n')[0] for f in blockedDomains]

with open('blockLists/blockedStartsWithUrl.txt', 'r') as fr:
    blockedStartsWithUrl = fr.readlines()
    blockedStartsWithUrl = [f.split('\n')[0] for f in blockedStartsWithUrl]

with open('blockLists/regexBlock.txt', 'r') as fr:
    regexBlock = fr.readlines()
    regexBlock = [f.split('\n')[0] for f in regexBlock]

# Create clones, so we can't just disable the single extension
for i in range(0, cloneCount):
    clonePath = os.path.join(scriptPath, "{}-{}-clone".format(extensionName, i))
    shutil.copytree(srcPath, clonePath)

    blockerJsPath = clonePath + '/blocker.js'
    with open(blockerJsPath, 'r') as original: data = original.read()

    writeUrlContent = """const alwaysAllowStartsWithUrl = {}
const blockAllTabsIfUrlOpen = {}
const blockedDomains = {}
const blockedStartsWithUrl = {}
const regexBlock = {}
""".format(alwaysAllowStartsWithUrl, blockAllTabsIfUrlOpen, blockedDomains, blockedStartsWithUrl, regexBlock)

    with open(blockerJsPath, 'w') as modified: modified.write(writeUrlContent + data)
