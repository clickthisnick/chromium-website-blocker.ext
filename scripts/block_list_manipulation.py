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
    This is just a small level of obfuscation so that we cannot look at our blocklists
        and see all the time consuming websites we are blocking
    """
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode("ascii")


def decode(message):
    base64_bytes = base64.b64decode(message)
    return base64_bytes.decode("ascii")


def decode_all():
    def get_domain_block_list():
        for blocklist in BLOCKLISTS:
            if blocklist.endswith("blockedDomains.txt"):
                with open(blocklist, "r", encoding="utf-8") as file_:
                    contents = file_.readlines()
                return contents
        return []

    # dict of file contents unencrypted
    contents = {}

    for file in BLOCKLISTS:
        contents[file] = []

        with open(file, "r", encoding="utf-8") as file_handle:
            file_content = file_handle.readlines()

        for line in file_content:
            # remove all whitespace
            value = line.strip()

            # "encrypted"
            if value.endswith(ENCRYPTED_ENDS_WITH):

                # Remove the encrypted indicator
                value = value[: -len(ENCRYPTED_ENDS_WITH)]
                value = decode(value)

            # remove all whitespace
            value = value.strip()

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

        # blockedRequestInitiator add all domains to list
        if file.endswith("blockedRequestInitiator.txt"):
            domain_block_list = get_domain_block_list()

            for domain_block in domain_block_list:
                if domain_block.endswith("\n"):
                    domain_block = domain_block[:-1]
                contents[file].append(f'https://www.{domain_block}": "true')
                contents[file].append(f'https://m.{domain_block}": "true')
                contents[file].append(f'https://{domain_block}": "true')
                contents[file].append(f'https://mobile.{domain_block}": "true')

        # write back the values but "encrypted" to the file
        contents_to_write = sorted(set(contents[file]))
        with open(file, "w", encoding="utf-8") as file_handle:
            for line in contents_to_write:
                file_handle.write(line)
                file_handle.write("\n")


def encode_all():
    # dict of file contents unencrypted
    contents = {}

    for file in BLOCKLISTS:
        contents[file] = []
        found_unencrpyted_value = False

        with open(file, "r", encoding="utf-8") as file_handle:
            file_content = file_handle.readlines()

        for line in file_content:
            # remove all whitespace
            value = line.strip()

            # "encrypted"
            if value.endswith(ENCRYPTED_ENDS_WITH):
                # Remove the encrypted indicator
                value = value[: -len(ENCRYPTED_ENDS_WITH)]
                value = decode(value)

            # not "encrypted"
            else:
                found_unencrpyted_value = True
                value = encode(line) + ENCRYPTED_ENDS_WITH + "\n"

            # remove all whitespace
            value = value.strip()

            contents[file].append(value)

        # write back the values but "encrypted" to the file
        if found_unencrpyted_value:
            with open(file, "w", encoding="utf-8") as file_handle:
                for line in contents[file]:
                    file_handle.write(line)
                    file_handle.write("\n")


decode_all()
encode_all()
