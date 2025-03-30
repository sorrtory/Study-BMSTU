#!/usr/bin/env python3

import time
import sys
k = 10
if len(sys.argv) > 1:
    k = int(sys.argv[1])

print(f"Sleeping for {k}..")
time.sleep(k);
