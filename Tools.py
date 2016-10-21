#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout, stdin, exit
import requests

def isNumber(s):
	try:
		int(s)
		return True
	except ValueError:
		try:
			import unicodedata
			unicodedata.numeric(s)
			return True
		except (TypeError, ValueError):
			return False
	except TypeError:
		pass

def readString (text):
        input_var = '.'
        if text != '':
                stdout.write ('  -> ' + text + ': ')
        while input_var != 'q':
                input_var = stdin.readline().split("\n")[0]
                if input_var.strip() == 'q':
                    exit (0)
                return input_var.strip()

def readInt (text):
        num = '.'
        while not isNumber (num):
                stdout.write ('  -> ' + text + ': ')
                num = readString ('')
                if not isNumber (num):
                        print ' -> "' + num + '" is not a number'
        return int(num)

def isValidHost (host):
	validHosts = ['streamcloud', 'nowvideo', 'streamplay', 'streamin', 'streaminto']

	if host.lower() in validHosts:
		return True

	return False
