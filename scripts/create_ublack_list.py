import os

SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))


def main():
    read_path = os.path.join(SCRIPTPATH, "../blockLists/blockedDomains.txt")
    write_path = os.path.join(SCRIPTPATH, "../blockLists/UBlackList.txt")

    with open(read_path, encoding="utf-8") as file_handle:
        lines = file_handle.readlines()

    block_list = []
    for line in lines:
        line = line.strip()
        block_list.append(f"*://www.{line}/*")
        block_list.append(f"*://m.{line}/*")
        block_list.append(f"*://mobile.{line}/*")
        block_list.append(f"*://platform.{line}/*")
        block_list.append(f"*://{line}/*")

    block_list_string = "\n".join(block_list)

    with open(write_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(block_list_string)


main()
