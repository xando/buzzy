import os
import sys
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
from jinja2 import Environment, FileSystemLoader


read = lambda n: codecs.open(n, encoding='utf-8').read()
write = lambda n,c: codecs.open(n, encoding='utf-8', mode="w").write(c)


def get_class():
    sys.path.append(os.getcwd())
    try:
        from main import StaticSite
        return StaticSite()
    except ImportError:
        return Base()


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


class render(object):
    register = []

    def __init__(self, func):
        self.func = func
        self.register.append(func.func_name)

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


class Base(object):

    BASE_DIR = path(os.getcwd())
    BUILD_DIR = 'build'
    TEMPLATES_DIR = 'templates'
    SERVER_PORT = 8000
    EXCLUDE = [
        '.git*', '*.py', '*.pyc', "%s/*" % BUILD_DIR, BUILD_DIR
    ]

    read = lambda self, n: read(n)
    write = lambda self, n,c: write(n, c)

    def template(self, template_name):
        env = Environment(loader=FileSystemLoader(self.TEMPLATES_DIR))
        return env.get_template(path(template_name))

    def render_template(self, template_name, **context):
        return self.template(template_name).render(**context)

    def _build(self):
        self.BUILD_DIR = path(self.BUILD_DIR)
        if self.BUILD_DIR.exists:
            [element.rm(r=True) for element in self.BUILD_DIR]
        else:
            self.BUILD_DIR.mkdir()

        self.renderers = [getattr(self, r)() for r in render.register]

        for m in memoized.register:
            m.cache = {}

        for f in path(self.BASE_DIR).ls():
            if not any([fnmatch.fnmatch(f.relative(self.BASE_DIR),pattern)
                        for pattern in self.EXCLUDE]):
                f.cp(self.BUILD_DIR / f.basename, r=True)

        render_objects = []
        for element in filter(lambda x:x, [r for r in self.renderers]):
            if type(element[0]) in [list, tuple]:
                render_objects.extend(element)
            else:
                render_objects.append(element)

        for name, content in render_objects:
            directory = path(name).dir()
            directory_build = self.BUILD_DIR / directory
            if directory and not directory_build.exists:
                directory_build.mkdir(p=True)
            self.write(self.BUILD_DIR / name, content)

        print "Generated %s" % datetime.now()

    def _watch(self):
        old_hash = ""

        while True:
            hash_elements = []
            for f in path(self.BASE_DIR).walk(r=True):
                if not any([fnmatch.fnmatch(f.relative(self.BASE_DIR),pattern)
                            for pattern in self.EXCLUDE]):
                    hash_elements.append(f.m_datetime.isoformat())
            current_hash =  hashlib.md5("".join(hash_elements)).hexdigest()
            if current_hash != old_hash:
                old_hash = current_hash
                self._build()
            time.sleep(0.2)

    def _server(self):
        os.chdir(self.BUILD_DIR)

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        httpd = SocketServer.ThreadingTCPServer(("", self.SERVER_PORT), Handler)

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
            (path(__file__).dir() / 'templates' / template).cp(path(os.getcwd()) / name, r=True)
        else:
            print "name required"


def main():
    if args.all:
        arg_0 = args.all[0]
        if arg_0 not in command.register:
            print "No such command '%s'" % arg_0
        else:
            getattr(get_class(), arg_0)(args)

if __name__ == "__main__":
    main()
