#!/usr/bin/env python
# -*- coding: utf-8 -*-

class InfoProvider ():
    def __init__ (self, name):
        self._name = name

    def getName (self):
        return self._name
