import argparse
import base64
import time
import requests
import subprocess
import json

API = "https://api.github.com/gists"
GISTS = ""
USER = ""
PASS = ""
FILE = "gistfile1.txt"
INTERVAL = 60


def write_to_file(file_content):
    path = "{0}/{1}".format(API, GISTS)
    data = {"files": {FILE: {"content": file_content}}}
    r = requests.patch(path, headers=HEADERS, data=json.dumps(data))
    if r.ok is not True:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Error occured: {0}".format(data))



def runCommand(command, content):
    try:
        call = subprocess.run(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True,
                              shell=True)

        output = "--empty--" if call.stdout.strip() == "" else call.stdout
    except Exception as e:
        print(e)
        output = str(e)
    content += "\n{0}".format(output)
    write_to_file(content)


def read_file():
    path = "{0}/{1}".format(API, GISTS)
    r = requests.get(path, headers=HEADERS)

    data = r.json()
    if r.ok is not True:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Error occured: {0}".format(data))

    files = data.get("files", None)
    file = files.get(FILE, None)

    try:
        content = file.get("content", None)
        if file.get("truncated", None):
            print("================= FILE IS TOO BIG =================")
            return

        lines = content.splitlines()
        if len(lines) == 0:
            print("================= GIST IS EMPTY =================")
        else:
            line = lines[-1]
            if line.startswith(">"):
                line = line[1:]
                print("Command detected: {0}".format(line.strip()))
                runCommand(line.strip(), content)
            else:
                print("No changes detected, waiting another {0} seconds".format(str(INTERVAL)))

    except KeyError:
        print("Error reading file with filename {0}".format(FILE))


print("================= Starting Bot =================")

parser = argparse.ArgumentParser()

parser.add_argument('--gists', type=str, required=True)
parser.add_argument('--user', type=str, required=True)
parser.add_argument('--token', type=str, required=True)
parser.add_argument('--file', type=str)
parser.add_argument('--interval', type=str)

args = parser.parse_args()

GISTS, USER, PASS = args.gists, args.user, args.token

if args.file is not None:
    FILE = args.file
if args.interval is not None:
    INTERVAL = int(args.interval)

HEADERS = {'Accept': 'application/vnd.github.v3+json',
           "Authorization": "Basic " + base64.urlsafe_b64encode("{0}:{1}".format(USER, PASS).encode()).decode()}

while True:
    read_file()
    print("WAITING...")
    time.sleep(INTERVAL)
