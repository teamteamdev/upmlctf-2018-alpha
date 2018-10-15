#!/usr/bin/env python3

import sys
import requests

ip = sys.argv[1]

r = requests.get("http://" + ip + "/get-flags/")
print(r.text)

