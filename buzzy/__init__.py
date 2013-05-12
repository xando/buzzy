import os
import sys
import time
import codecs
import hashlib
import inspect
import fnmatch
import argparse
import SimpleHTTPServer
import SocketServer

from osome import path
from functools import partial
from collections import Hashable
from datetime import datetime
from multiprocessing import Process


read = lambda n: codecs.open(n, encoding='utf-8').read()
write = lambda n,c: codecs.open(n, encoding='utf-8', mode="w").write(c)


def get_class():
    sys.path.append(os.getcwd())
    from hive import StaticSite
    return StaticSite()


class memoized(object):
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, Hashable):
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        return self.func.__doc__

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)


class render(object):
    def __init__(self, *args):
        self.args = args

    def __call__(self, args):
        if not inspect.isfunction(args):
            return self.args[0](args)
        def wrapped_f(cls):
            return args(cls, *[ path(a).relative(cls.BASE_DIR) for a in self.args])
        wrapped_f.render = True
        return wrapped_f


class Base(object):

    _register = []

    BASE_DIR = path(os.getcwd())
    BUILD_DIR = 'build'
    SERVER_PORT = 8000
    EXCLUDE = [
        '.git*', '*.py', '*.pyc', "%s/*" % BUILD_DIR, BUILD_DIR
    ]

    read = lambda self, n: read(n)
    write = lambda self, n,c: write(n, c)

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        atributes = [getattr(self,a) for a in dir(self)]

        self.renderers = [
            func() for func in atributes if hasattr(func, 'render')
        ]
        self.renderers.extend([
            func(self) for func in atributes if isinstance(func, render)
        ])


    def build(self):
        self.BUILD_DIR = path(self.BUILD_DIR)
        if self.BUILD_DIR.exists:
            [element.rm(r=True) for element in self.BUILD_DIR]
        else:
            self.BUILD_DIR.mkdir()

        for f in path(self.BASE_DIR).ls():
            if not any([fnmatch.fnmatch(f.relative(self.BASE_DIR),pattern)
                        for pattern in self.EXCLUDE]):
                f.cp(self.BUILD_DIR / f.basename, r=True)

        render_objects = []
        for element in filter(lambda x:x, [r for r in self.renderers]):
            if type(element) in [list, tuple]:
                render_objects.extend(element)
            else:
                render_objects.append(element)

        for element in render_objects:
            directory = path(element['name']).dir()
            directory_build = self.BUILD_DIR / directory
            if directory and not directory_build.exists:
                directory_build.mkdir(p=True)
            self.write(self.BUILD_DIR / element['name'], element['content'])

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
                self.build()
            time.sleep(0.2)

    def _server(self):
        os.chdir(self.BUILD_DIR)

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        httpd = SocketServer.ThreadingTCPServer(("", self.SERVER_PORT), Handler)

        print "serving at port %s" % self.SERVER_PORT
        httpd.serve_forever()

    def server(self):
        watch = Process(target=self._watch)
        watch.start()
        server = Process(target=self._server)
        server.start()

        try:
            watch.join()
            server.join()
        except KeyboardInterrupt:
            server.terminate()
            watch.terminate()


def server(args):
    get_class().server()


def build(args):
    get_class().build()


def create(args):
    blog_dir = (os.getcwd() / args.name).mkdir()
    package_dir = path(__file__).dir()

    (package_dir / 'index.html').cp(blog_dir / 'index.html')
    (package_dir / 'libs').cp(blog_dir / 'libs', r=True)
    (package_dir / 'posts').cp(blog_dir / 'posts', r=True)
    (package_dir / 'img').cp(blog_dir / 'img', r=True)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser('create')
    parser_create.add_argument('name', type=str, help='name')
    parser_create.set_defaults(func=create)

    parser_build = subparsers.add_parser('build')
    parser_build.set_defaults(func=build)

    parser_server = subparsers.add_parser('server')
    parser_server.set_defaults(func=server)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
