# Generates multiple clones of the same extension to load on Chrome

import os
import shutil
import string
import random
from block_list_manipulation import (
    SCRIPTPATH,
    BLOCKLISTS,
    ENCRYPTED_ENDS_WITH,
    encode,
    decode,
)


def generate_block_code():
    # dict of file contents unencrypted
    contents = {}

    for file in BLOCKLISTS:
        contents[file] = []
        found_unencrpyted_value = False

        with open(file, "r", encoding="utf-8") as file_handle:
            file_content = file_handle.readlines()

        for i, line in enumerate(file_content):
            if line.endswith("\n"):
                value = line[:-1]
            else:
                value = line

            # "encrypted"
            if value.endswith(ENCRYPTED_ENDS_WITH):
                # Remove the encrypted indicator
                value = value[: -len(ENCRYPTED_ENDS_WITH)]
                value = decode(value)

            # not "encrypted"
            else:
                found_unencrpyted_value = True
                file_content[i] = encode(line) + ENCRYPTED_ENDS_WITH + "\n"

            if value.endswith("\n"):
                value = value[:-1]

            contents[file].append(value)

        # write back the values but "encrypted" to the file
        if found_unencrpyted_value:
            with open(file, "w", encoding="utf-8") as file_handle:
                for line in file_content:
                    file_handle.write(line)

    # Create clones, so we can't just disable the single extension
    write_url_content = ""

    var_to_contents = {
        "const alwaysAllowStartsWithUrl = [": contents[BLOCKLISTS[0]],
        "const blockAllTabsIfUrlOpen = [": contents[BLOCKLISTS[1]],
        "const blockedDomains = [": contents[BLOCKLISTS[2]],
        "const blockedStartsWithUrl = [": contents[BLOCKLISTS[3]],
        "const regexBlock = [": contents[BLOCKLISTS[4]],
        "const blockedRequestInitiator = {": contents[BLOCKLISTS[5]],
    }

    for var, content in var_to_contents.items():
        text = "','".join(content)
        write_url_content += var
        if text:
            write_url_content += f"'{text}'"
        write_url_content += "]\n"

    return write_url_content


def generate_all_clones(dist_path, src_path, extension_name, write_url_content):
    clone_count = 30

    # remove the existing dict folder
    try:
        shutil.rmtree(dist_path)
    except Exception:  # pylint:disable=broad-except
        pass

    os.mkdir(dist_path)

    extension_loading_string = ""
    letters = string.ascii_letters

    for i in range(0, clone_count):
        if i == 1:
            clone_path = os.path.join(dist_path, "extensions", "astatic")
        else:
            clone_path = os.path.join(
                dist_path,
                "extensions",
                f'{extension_name + "".join(random.choice(letters) for i in range(21))}-{i}-clone',
            )
        shutil.copytree(src_path, clone_path)

        blocker_js_path = os.path.join(clone_path, "background.js")

        with open(blocker_js_path, "r", encoding="utf-8") as original:
            data = original.read()
        with open(blocker_js_path, "w", encoding="utf-8") as modified:
            modified.write(write_url_content + data)
        extension_loading_string += f"{clone_path},"

    # Remove the final comma
    extension_loading_string = extension_loading_string[:-1]


def main():
    # Script Path
    dist_path = os.path.join(SCRIPTPATH, "../", "dist")

    # Extension Name
    extension_name = SCRIPTPATH.split("/")[-2]

    # Src Path
    src_path = os.path.join(SCRIPTPATH, "../src")

    # Generate block code
    write_url_content = generate_block_code()

    generate_all_clones(dist_path, src_path, extension_name, write_url_content)


main()
