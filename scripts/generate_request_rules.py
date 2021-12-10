import os
import json

SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))

read_path = os.path.join(SCRIPTPATH, "../blockLists/blockedDomains.txt")
rule_template_path = os.path.join(SCRIPTPATH, "../src/rules_template.json")
rule_path = os.path.join(SCRIPTPATH, "../src/rules_generated.json")

with open(read_path, encoding="utf-8") as f:
    lines = f.readlines()

with open(rule_template_path, encoding="utf-8") as rules_template:
    rules = json.load(rules_template)

for line in lines:
    line = line.strip()
    rules[0]["condition"]["domains"].append(line)

with open(rule_path, "w", encoding="utf-8") as f:
    json.dump(rules, f, indent=2)
