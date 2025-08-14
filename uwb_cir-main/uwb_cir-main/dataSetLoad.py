# -*- coding: euc-kr -*-
import json
import sys

with open(sys.argv[1], 'r') as file:
	dataSet = json.load(file)
