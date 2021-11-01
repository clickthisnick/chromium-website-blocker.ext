import os
import base64

ENCRYPTED_ENDS_WITH = "SCRIPT-ENCODED"
SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))
BLOCKLISTS = [
    f"{SCRIPTPATH}/../blockLists/alwaysAllowStartsWithUrl.txt",
    f"{SCRIPTPATH}/../blockLists/blockAllTabsIfUrlOpen.txt",
    f"{SCRIPTPATH}/../blockLists/blockedDomains.txt",
    f"{SCRIPTPATH}/../blockLists/blockedStartsWithUrl.txt",
    f"{SCRIPTPATH}/../blockLists/regexBlock.txt",
    f"{SCRIPTPATH}/../blockLists/blockedRequestInitiator.txt",
]


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


def decodeAll():
    def get_domain_block_list():
        for blocklist in BLOCKLISTS:
            if blocklist.endswith("blockedDomains.txt"):
                with open(blocklist, "r", encoding="utf-8") as file_:
                    contents = file_.readlines()
                return contents

    # dict of file contents unencrypted
    contents = {}

    for file in BLOCKLISTS:
        contents[file] = []

        with open(file, "r") as fr:
            fileContent = fr.readlines()

        for i, f in enumerate(fileContent):
            if f.endswith("\n"):
                value = f[:-1]
            else:
                value = f

            # "encrypted"
            if value.endswith(ENCRYPTED_ENDS_WITH):

                # Remove the encrypted indicator
                value = value[: -len(ENCRYPTED_ENDS_WITH)]
                value = decode(value)

            if value.endswith("\n"):
                value = value[:-1]

            contents[file].append(value)

        # Make it so we can't search for the sites we are blocking
        if file.endswith("blockedStartsWithUrl.txt"):
            domain_block_list = get_domain_block_list()

            for domain_block in domain_block_list:
                if domain_block.endswith("\n"):
                    domain_block = domain_block[:-1]
                contents[file].append(
                    f"https://www.google.com/search?q={domain_block}&"
                )
                contents[file].append(
                    f"https://www.google.com/search?q={domain_block.split('.')[0]}&"
                )
                contents[file].append(f"https://duckduckgo.com/?q={domain_block}&")
                contents[file].append(
                    f"https://duckduckgo.com/?q={domain_block.split('.')[0]}&"
                )

        # write back the values but "encrypted" to the file
        contents_to_write = sorted(set(contents[file]))
        with open(file, "w") as fr:
            for x in contents_to_write:
                fr.write(x)
                fr.write("\n")


def encodeAll():
    # dict of file contents unencrypted
    contents = {}

    for file in BLOCKLISTS:
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
            if value.endswith(ENCRYPTED_ENDS_WITH):
                # Remove the encrypted indicator
                value = value[: -len(ENCRYPTED_ENDS_WITH)]
                value = decode(value)

            # not "encrypted"
            else:
                foundUnencrpytedValue = True
                value = encode(f) + ENCRYPTED_ENDS_WITH + "\n"

            if value.endswith("\n"):
                value = value[:-1]

            contents[file].append(value)

        # write back the values but "encrypted" to the file
        if foundUnencrpytedValue:
            with open(file, "w") as fr:
                for x in contents[file]:
                    fr.write(x)
                    fr.write("\n")


decodeAll()
encodeAll()
