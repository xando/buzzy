import os
import time
import args
import codecs

import hashlib
import fnmatch
import SimpleHTTPServer
import SocketServer

from osome import path
from functools import partial
from collections import Hashable
from datetime import datetime
from multiprocessing import Process


from buzzy import render


class register(object):
    elements = []

    def __init__(self, func):
        self.func = func
        self.elements.append(func.func_name)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)


class command(object):
    register = []

    def __init__(self, func):
        self.func = func
        self.register.append(func.func_name)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)


class memoized(object):
    register = []

    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.register.append(self)

    def __call__(self, *args):
        if not isinstance(args, Hashable):
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)


class Base(object):

    INCLUDE = []
    BASE_DIR = path(os.getcwd())
    BUILD_DIR = '_build'
    TEMPLATES_DIR = 'templates'
    SERVER_PORT = 8000
    WATCH_EXCLUDE = [
        '.git*', '*.py', '*.pyc'
    ]

    def __init__(self):
        self.WATCH_EXCLUDE.extend(["%s/*" % self.BUILD_DIR, self.BUILD_DIR])
        self.BUILD_DIR = path(self.BUILD_DIR)

        render.render.klass = self
        arg_0 = args.all[0]
        if arg_0 not in command.register:
            print "No such command '%s'" % arg_0
        else:
            getattr(self, arg_0)(args)


    def _ensure_path(self, name):
        directory = path(name).dir()
        directory_build = self.BUILD_DIR / directory
        if directory and not directory_build.exists:
            directory_build.mkdir(p=True)

    def write(self, name, content):
        self._ensure_path(name)
        codecs.open(
            self.BUILD_DIR / name, encoding='utf-8', mode="w"
        ).write(content)

    def _clean_memoized(self):
        for m in memoized.register:
            m.cache = {}

    def _clean_build_dir(self):
        if self.BUILD_DIR.exists:
            [element.rm(r=True) for element in self.BUILD_DIR]
        else:
            self.BUILD_DIR.mkdir()

    def _include(self):
        for element in self.INCLUDE:
            path(element).cp(self.BUILD_DIR / element, r=True)

    def _build(self):
        self._clean_memoized()
        self._clean_build_dir()
        self._include()

        for func in register.elements:
            for renderer in getattr(self, func)():
                self.write(renderer.name, renderer.content)

        print "Generated %s" % datetime.now()

    def _watch(self):
        to_watch = lambda x: not any([
            fnmatch.fnmatch(x.relative(self.BASE_DIR), pattern)
            for pattern in self.WATCH_EXCLUDE
        ])

        files = {}

        while True:
            changed = []
            for element in path(self.BASE_DIR).walk(r=True):
                element = element.relative(self.BASE_DIR)
                if to_watch(element):

                    value = files.get(element)
                    if value != element.m_datetime.isoformat():
                        changed.append(element)
                        files[element] = element.m_datetime.isoformat()

            if changed:
                self._build()

            time.sleep(0.2)

    def _server(self):
        self._build()
        os.chdir(self.BUILD_DIR)

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        httpd = SocketServer.ThreadingTCPServer(
            ("", self.SERVER_PORT), Handler
        )

        print "serving at port %s" % self.SERVER_PORT
        httpd.serve_forever()

    @command
    def build(self, args):
        self._build()

    @command
    def watch(self, args):
        self._watch()

    @command
    def server(self, args):
        server = Process(target=self._server)
        server.start()

        try:
            if '--no-watch' not in args.flags:
                self._watch()
        except KeyboardInterrupt:
            server.terminate()

    @command
    def create(self, args):

        if len(args.all) > 2:
            template = args.all[2]
        else:
            template = 'basic'

        if len(args.all) > 1:
            name = args.all[1]
            (path(__file__).dir() / 'templates' / template).cp(
                path(os.getcwd()) / name, r=True
            )
        else:
            print "name required"
