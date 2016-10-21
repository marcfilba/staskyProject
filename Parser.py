#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser

class HTMLTree(object):
    def __init__(self):
        self._childs = []

    def _get_by_level(self, list_, tag = None, id = None, clazz = None):
        ret = list_
        if tag != None:
            ret = [e for e in ret if e.tag == tag]
        if id != None:
            ret = [e for e in ret if 'id' in e.attrs and id in e.attrs['id']]
        if clazz != None:
            ret = [e for e in ret if 'class' in e.attrs and clazz in e.attrs['class']]
        return ret

    def _get_by_rec(self, list_, tag = None, id = None, clazz = None):
        ret = []
        for parent in list_:
            ret += self._get_by_rec(parent._childs,tag,id,clazz)
        ret += self._get_by_level(list_,tag,id,clazz)
        return ret

    def get_by(self, tag = None, id = None, clazz = None):
        return self._get_by_rec(self._childs, tag, id, clazz)

    def get_first_by(self, tag = None, id = None, clazz = None):
        r = self.get_by(tag, id, clazz)
        if len(r) > 0:
            return r[0]
        return None

    def get_childs (self):
        return self._childs


class HTMLWrapper(HTMLTree):
    def __init__(self):
        HTMLTree.__init__(self)

    @property
    def html(self):
        return self._childs

    def add(self, elem):
        self._childs.append(elem)


class HTMLElement(HTMLTree):
    def __init__(self, tag = ''):
        self._tag = tag
        self._attrs = {'data':[]}
        HTMLTree.__init__(self)

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag):
        self._tag = tag

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, attrs):
        for elem in attrs:
            self._attrs.setdefault(elem[0], [])
            if len(elem) > 1: self._attrs[elem[0]].append(elem[1])
            else: self._attrs[elem[0]].append('')

    @property
    def data(self):
        return self._attrs['data']

    @data.setter
    def data(self, data):
        self._attrs['data'].append(data)

    def add_child(self, child):
        self._childs.append(child)

    @property
    def childs(self):
        return self._childs

    @childs.setter
    def childs(self, childs):
        for child in childs:
            self.add_child(child)

    def __repr__(self):
        body = '<{0} {1}>{2}</{0}>'.format(self._tag,
                                           ' '.join(['{0}="{1}"'.format(k,d) for k in self._attrs if k != 'data' for d in self._attrs[k]]),
                                           ''.join(self._attrs['data']))
        return body

    def __str__(self):
        return self.__repr__()


class Parser(HTMLParser):
    def __init__(self):
        self.data = 0
        self.start = 0
        self.startend = 0
        self.end = 0
        self.decl = 0
        self.comment = 0
        self.content = HTMLWrapper()
        self.stack = []
        HTMLParser.__init__(self)

    @property
    def content(self):
        return self.content

    #def feed(self, data, encoding):
    def feed(self, data):
        self.__init__()
        #self.encoding = encoding
        HTMLParser.feed(self, data)
        return self.content

    def handle_data(self, data):
        if len(self.stack) > 0:
            self.data += 1
            #self.stack[-1].data = data.encode(self.encoding, 'replace')
            self.stack[-1].data = data.strip()

    def handle_starttag(self, tag, attrs):
        self.start += 1
        elem = HTMLElement(tag)
        elem.attrs = attrs
        self.stack.append(elem)

    def handle_startendtag(self, tag, attrs):
        self.startend += 1
        elem = HTMLElement(tag)
        elem.attrs = attrs
        if len(self.stack) > 0:
            self.stack[-1].add_child(elem)

    def handle_endtag(self, tag):
        self.end += 1
        if tag in [e.tag for e in self.stack]:
            childs = []
            while len(self.stack) > 0 and self.stack[-1].tag != tag:
                elem = self.stack.pop()
                childs.append(elem)
            else:
                if len(self.stack) > 0:
                    elem = self.stack.pop()
                    elem.childs = childs
                    if len(self.stack) > 0: self.stack[-1].add_child(elem)
                    else: self.content.add(elem)
        #else:
        #    print("ERROR: tag out of scope! - Out of the Stack")

    def handle_decl(self, decl):
        self.decl += 1
        elem = HTMLElement('declaration')
        elem.data = decl
        self.content.add(elem)

    def handle_comment(self, data):
        self.comment += 1
        elem = HTMLElement('comment')
        elem.data = data
        self.content.add(elem)

    def print_statistics(self):
        print("Start Tags:\t\t", self.start)
        print("Start-End Tags:\t", self.startend)
        print("End Tags:\t\t", self.end)
        print("Data Tags:\t\t", self.data)
        print("Decl Tags:\t\t", self.decl)
        print("Comment Tags:\t", self.comment)


def analyze(listelements):
    for key, e in enumerate(listelements):
        print('Parent',str(key)+':')
        print(e)
        print('Child:')
        print(e.childs)
        print('----------------------------')
