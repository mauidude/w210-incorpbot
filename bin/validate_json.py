#!/usr/bin/env python3
import glob
import json
import sys

for file in glob.glob('data/*.json'):
    with open(file) as f:
        try:
            json.load(f)
        except Exception as e:
            print("%s is not valid JSON:" % file)
            print(e)
            sys.exit(1)
