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

PORT = 3333


def generate_string(len = 16, alph = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join([random.choice(alph) for _ in range(len)])


def throw(errno, message=""):
    print >> sys.stderr, message
    sys.exit(errno)
    

class Status:
    OK            = 101
    CORRUPT       = 102
    MUMBLE        = 103
    DOWN          = 104
    CHECKER_ERROR = 110
    
    
def socket_put(ip, key=None, value=None):
    if key is None:
        key = generate_string(32)
    if value is None:
        value = generate_string(32)
    
    r = remote(ip, PORT, timeout=1.5)
    
    data = r.recvuntil("?\n")
    if not "Put/get?" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    r.sendline("put")
    
    data = r.recvuntil("?\n")
    if not "Token?" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    r.sendline(key)
    
    data = r.recvuntil("?\n")
    if not "Secret?" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    r.sendline(value)
    
    data = r.recvuntil("!\n")
    if not "OK!" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    r.close()
    
    return key, value
    
    
def socket_get(ip, key):
    r = remote(ip, PORT, timeout=1.5)
    
    data = r.recvuntil("?\n")
    if not "Put/get?" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    r.sendline("get")
    
    data = r.recvuntil("?\n")
    if not "Token?" in data:
        throw(Status.MUMBLE, "Invalid response")
    
    r.sendline(key)
    
    data = r.recvall(timeout=1.5)
    flag = re.search("Your secret:\n(.+)\n", data)
    if flag is None:
        throw(Status.CORRUPT, "Can't get saved note")
    flag = flag.group(1)
    
    return flag
    
    
def check(ip):
    key, value = socket_put(ip)
    saved_value = socket_get(ip, key)
    
    if value != saved_value:
        throw(Status.CORRUPT, "Can't get saved note")
    
    throw(Status.OK)


def put(ip, flag):
    key, value = socket_put(ip, value=flag)
    
    print(key)
    
    throw(Status.OK)


def get(ip, flag_id, flag):
    value = socket_get(ip, flag_id)
    
    if value != flag:
        throw(Status.CORRUPT, "Can't get saved note")
    
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
