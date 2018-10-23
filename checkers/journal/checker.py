#!/usr/bin/env python

import sys
argv = sys.argv[1:]

import socket
from pwn import *
import string
import random
import re
import traceback

context.log_level = 'critical'

PORT = 1428


def generate_string(len = 16, alph = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join([random.choice(alph) for _ in range(len)])
    

def throw(errno, message=""):
    print message
    sys.exit(errno)
    

class Status:
    OK            = 101
    CORRUPT       = 102
    MUMBLE        = 103
    DOWN          = 104
    CHECKER_ERROR = 110
    
    
def register(conn):
    data = conn.recvuntil("> ")
    if not "Electric Journal" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    conn.sendline("1")
    
    data = conn.recvuntil("> ")
    if not "Enter desired username" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    username = generate_string(16)
    
    conn.sendline(username)
    
    data = conn.recvuntil("actions:")
    token = re.search("token: ([A-Z0-9]+)", data)
    if token is None:
        throw(Status.MUMBLE, "Can't obtain token")
    token = token.group(1)
    
    return (username, token)

    
def login(conn, username, token):
    data = conn.recvuntil("> ")
    if not "Electric Journal" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    conn.sendline("2")
    conn.recvuntil("> ")
    conn.sendline(token)
    
    data = conn.recvuntil("actions:")
    
    if not username in data:
        throw(Status.MUMBLE, "Can't login")
        
        
def create_ass(conn, assignment=None):
    if assignment is None:
        assignment = generate_string(32)
    
    data = conn.recvuntil("> ")
    if not "Create an assignment" in data:
        throw(Status.MUMBLE, "Broken menu")
    
    conn.sendline("1")
    
    data = conn.recvuntil("> ")
    if not "assignment" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    conn.sendline(assignment)
    
    data = conn.recvuntil("actions:")
    token = re.search("key is ([A-Z0-9]+)", data)
    if token is None:
        throw(Status.MUMBLE, "Can't obtain assignment key")
    token = token.group(1)
    
    return (token, assignment)


def read_ass(conn, token):
    data = conn.recvuntil("> ")
    if not "Open an assignment" in data:
        throw(Status.MUMBLE, "Broken menu")
    
    conn.sendline("2")
    
    data = conn.recvuntil("> ")
    if not "key" in data:
        throw(Status.MUMBLE, "Invalid response")

    conn.sendline(token)
    data = conn.recvuntil("actions:")
    task = re.search("assignment: (.+)\n", data)
    if task is None:
        throw(Status.CORRUPT, "Can't retrieve the assignment")
    task = task.group(1)
    
    return task
    
    
def lookup_user(conn, username):
    data = conn.recvuntil("> ")
    if not "List of users" in data:
        throw(Status.MUMBLE, "Broken menu")
    
    conn.sendline("3")
    
    data = conn.recvuntil("actions:")
    
    if not username in data:
        throw(Status.MUMBLE, "Broken user list")

    
def lookup_my_ass(conn, token):
    data = conn.recvuntil("> ")
    if not "My assignments" in data:
        throw(Status.MUMBLE, "Broken menu")
    
    conn.sendline("4")
    
    data = conn.recvuntil("actions:")
    if not token in data:
        throw(Status.MUMBLE, "Assignment not found")

        
def close(conn):
    conn.sendline("0")
    conn.shutdown()
    
    data = conn.recvall()
    
    if not "Bye" in data:
        throw(Status.MUMBLE, "Can't exit")
    
    conn.close()


def check(ip):
    r = remote(ip, PORT, timeout=1.5)
    
    username, token = register(r)
    close(r)
    
    r = remote(ip, PORT, timeout=3)
    
    login(r, username, token)
    
    key, note = create_ass(r)
    saved_note = read_ass(r, key)
    
    if note != saved_note:
        throw(Status.MUMBLE, "Can't save the note")
    
    lookup_user(r, username)
    
    close(r)

    throw(Status.OK)


def put(ip, flag):
    r = remote(ip, PORT, timeout=3)
    
    username, token = register(r)
    
    key, note = create_ass(r, flag)
    
    print(key)
    
    saved_note = read_ass(r, key)
    
    if note != saved_note:
        throw(Status.MUMBLE, "Can't save the flag")
    
    lookup_my_ass(r, key)
    
    close(r)
    
    throw(Status.OK)


def get(ip, flag_id, flag):
    r = remote(ip, PORT, timeout=3)
    
    username, token = register(r)
    
    saved_note = read_ass(r, flag_id)
    
    if saved_note != flag:
        throw(Status.CORRUPT, "Wrong flag")
    
    close(r)
    
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
    except (socket.error, socket.timeout, PwnlibException, EOFError) as e:
        throw(Status.DOWN, "Exception " + str(e))
    except Exception as e:
        traceback.print_exc()
        throw(Status.CHECKER_ERROR, "Exception in checker")
