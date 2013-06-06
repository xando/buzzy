import os
import time
import args

import hashlib
import fnmatch
import SimpleHTTPServer
import SocketServer

from osome import path
from functools import partial
from collections import Hashable
from datetime import datetime
from multiprocessing import Process
from jinja2 import Environment, FileSystemLoader

from buzzy import render


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


class command(object):
    register = []

    def __init__(self, func):
        self.func = func
        self.register.append(func.func_name)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)


class Base(object):

    BASE_DIR = path(os.getcwd())
    BUILD_DIR = 'build'
    TEMPLATES_DIR = 'templates'
    SERVER_PORT = 8000
    EXCLUDE = [
        '.git*', '*.py', '*.pyc', "%s/*" % BUILD_DIR, BUILD_DIR
    ]

    def __init__(self):
        render.render.klass = self
        arg_0 = args.all[0]
        if arg_0 not in command.register:
            print "No such command '%s'" % arg_0
        else:
            getattr(self, arg_0)(args)

    def template(self, template_name):
        env = Environment(loader=FileSystemLoader(self.TEMPLATES_DIR))
        return env.get_template(path(template_name))

    def render_template(self, template_name, **context):
        return self.template(template_name).render(**context)

    def _clean_memoized(self):
        for m in memoized.register:
            m.cache = {}

    def _clean_build_dir(self):
        self.BUILD_DIR = path(self.BUILD_DIR)
        if self.BUILD_DIR.exists:
            [element.rm(r=True) for element in self.BUILD_DIR]
        else:
            self.BUILD_DIR.mkdir()

    def _build(self):
        self._clean_memoized()
        self._clean_build_dir()

        for name in render.register:
            getattr(self, name)()

        print "Generated %s" % datetime.now()

    def _watch(self):
        old_hash = ""

        while True:
            hash_elements = []
            for f in path(self.BASE_DIR).walk(r=True):
                if not any([fnmatch.fnmatch(f.relative(self.BASE_DIR), pattern)
                            for pattern in self.EXCLUDE]):
                    hash_elements.append(f.m_datetime.isoformat())
            current_hash = hashlib.md5("".join(hash_elements)).hexdigest()
            if current_hash != old_hash:
                old_hash = current_hash
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
