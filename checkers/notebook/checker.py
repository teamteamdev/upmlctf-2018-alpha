#!/usr/bin/python3
import requests, random, string, sys


OK = 101
NO_FLAG = 102
MUMBLE = 103
NO_CONNECT = 104
CHECKER_ERROR = 110


def generate_string(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


def check(ip):
    try:
        r = requests.get('http://' + ip + ":8616", timeout=5)
    except requests.exceptions.Timeout as e:
        return {"status": NO_CONNECT, "error": "Got a timeout while accessing server."}
    except:
        return {"status": NO_CONNECT, "error": "Could not access server."}

    if r.status_code != 200:
        return {"status": NO_CONNECT, "error": "Could not access server."}
    if r.headers["Content-Type"] != "text/html; charset=utf-8":
        return {"status": MUMBLE, "error": "Page content is corrupted"}
    if "n0t3b00k" not in r.text:
        return {"status": MUMBLE, "error": "Page content is corrupted."}
    return {"status": OK}


def put(ip, flag_id, flag):
    flag_id = generate_string(10)
    key = generate_string(10)
    payload = {'note-name': flag_id, 'text': flag, 'key': key}

    try:
        r = requests.post('http://%s:8616/create' % ip, data=payload, timeout=5)
    except requests.exceptions.Timeout as e:
        return {"status": NO_CONNECT, "error": "Got a timeout while accessing server.", "flag_id": flag_id, "key": key}
    except:
        return {"status": NO_CONNECT, "error": "Could not access server.", "flag_id": flag_id, "key": key}

    if r.text != "Note successfully created!":
        return {"status": MUMBLE, "error": "Got an unexpected response.", "flag_id": flag_id, "key": key}
    return {"status": OK, "flag_id": flag_id, "key": key}


def get(ip, flag_id, flag):
    flag_id, key = flag_id.split('.')
    payload = {'note-name': flag_id, 'key': key}
    
    try:
        r = requests.post('http://%s:8616/note' % ip, data=payload, timeout=5)
    except requests.exceptions.Timeout as e:
        return {"status": NO_CONNECT, "error": "Got a timeout while accessing server."}
    except:
        return {"status": NO_CONNECT, "error": "Could not access server."}
    try:
        text = str(r.text)
    except:
        return {"status": MUMBLE, "error": "Doesn't return flag properly."}
    if str(r.text) != flag:
        return {"status": NO_FLAG, "error": "Flag doesn't exist or changed."}
    return {"status": OK}


if __name__ == "__main__":
    args = sys.argv
    args = args[1:]
    if args[0] == "check":
        ip = args[1]
        r = check(ip)
        if r["status"] != OK:
            print(r["error"], file=sys.stderr)
        exit(r["status"])
    if args[0] == "put":
        ip, flag_id, flag = args[1], args[2], args[3]
        r = put(ip, flag_id, flag)
        print(r["flag_id"] + "." + r["key"])
        if r["status"] != OK:
            print(r["error"], file=sys.stderr)
        exit(r["status"])
    if args[0] == "get":
        ip, flag_id, flag = args[1], args[2], args[3]
        r = get(ip, flag_id, flag)
        if r["status"] != OK:
            print(r["error"], file=sys.stderr)
        exit(r["status"])

