#!/usr/bin/env python3

import sys
argv = sys.argv[1:]
import requests
import string
import random
import traceback
import os


class Status:
    OK            = 101
    CORRUPT       = 102
    MUMBLE        = 103
    DOWN          = 104
    CHECKER_ERROR = 110
    
    
def throw(errno, message=""):
    print(message, file=sys.stderr)
    sys.exit(errno)
    
    
def generate_string(len = 16, alph = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join([random.choice(alph) for _ in range(len)])


def signup(ip):
    email = generate_string(8, string.ascii_lowercase) + "@" + generate_string(6, string.ascii_lowercase) + "." + random.choice(["org", "com", "net", "ru"])
    username = generate_string(10)
    password = generate_string(10)
    
    r = requests.post("http://{ip}:3000/signup".format(ip=ip), data={"email": email, "name": username, "password": password}, timeout=0.5)
    
    if not "Hackergrom" in r.text:
        throw(Status.MUMBLE, "Invalid response")
    
    return (email, username, password)


def signin(ip, email, username, password):
    s = requests.Session()
    
    r = s.post("http://{ip}:3000/signin".format(ip=ip), data={"email": email, "password": password}, timeout=0.5)
    
    r.raise_for_status()
    
    if not username in r.text:
        throw(Status.MUMBLE, "Invalid response")
    
    return s
    

def upload(ip, session, text=None):
    if text is None:
        text = generate_string(32)
    
    photo = random.choice(os.listdir("/home/ctf/hacker_pics/"))
    
    r = session.post(
        "http://{ip}:3000/new".format(ip=ip),
        data={"text": text},
        files={"pic": open("/home/ctf/hacker_pics/" + photo, "rb")}
    )
    
    r.raise_for_status()
    
    if not text in r.text:
        throw(Status.MUMBLE, "Invalid response")


def check(ip):
    r = requests.get("http://{ip}:3000/signin".format(ip=ip), timeout=0.5)
    
    if not "Sign in" in r.text:
        throw(Status.MUMBLE, "Invalid response")
    
    r = requests.get("http://{ip}:3000/signup".format(ip=ip), timeout=0.5)
    
    if not "Sign up" in r.text:
        throw(Status.MUMBLE, "Invalid response")
    
    email, uname, passw = signup(ip)
    ses = signin(ip, email, uname, passw)
    
    r = ses.get("http://{ip}:3000/new".format(ip=ip), timeout=0.5)
    if not "New post" in r.text:
        throw(Status.MUMBLE, "Invalid response")
    
    upload(ip, ses)
    throw(Status.OK)


def put(ip, flag):
    email, uname, passw = signup(ip)
    print(email, uname, passw, sep="_")
    ses = signin(ip, email, uname, passw)
    upload(ip, ses, flag)
    throw(Status.OK)


def get(ip, flag_id, flag):
    email, uname, passw = flag_id.split("_")
    ses = signin(ip, email, uname, passw)
    
    main = ses.get("http://{ip}:3000/".format(ip=ip), timeout=0.5)
    
    if not flag in main.text:
        throw(Status.CORRUPT, "No flag")
    
    throw(Status.OK)


if __name__ == "__main__":
    try:
        if argv[0] == "check":
            ip = argv[1]
            check(ip)
        elif argv[0] == "put":
            ip, flag = argv[1], argv[3]
            put(ip, flag)
        elif argv[0] == "get":
            ip, flag_id, flag = argv[1], argv[2], argv[3]
            get(ip, flag_id, flag)
        else:
            throw(Status.CHECKER_ERROR, "Unknown command %s" % argv[0])
            
        throw(Status.CHECKER_ERROR, "Checker didn't throw status")
    except requests.exceptions.RequestException as e:
        throw(Status.DOWN, "Exception " + str(e))
    except Exception as e:
        traceback.print_exc()
        throw(Status.CHECKER_ERROR, "Exception in checker")
