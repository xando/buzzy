import os
import time
import codecs
import argparse
import logging
import SimpleHTTPServer
import SocketServer

from watchdog.observers.polling import PollingObserver as Observer

from functools import partial
from multiprocessing import Process
from watchdog.events import PatternMatchingEventHandler

from buzzy import render, log
from buzzy.path import path


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
        self.register.append(self)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)


class Base(object):

    INCLUDE = []
    BASE_DIR = path(os.getcwd())
    BUILD_DIR = '_build'
    TEMPLATES_DIR = 'templates'
    SERVER_PORT = 8000
    WATCH_EXCLUDE = ['.git*', '.hg*', '*.orig']

    LOG_NAME = None
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_HANDLERS = [log.ColorizingStreamHandler()]
    LOG_LEVERL = logging.INFO

    def __init__(self):

        self.logger = logging.getLogger(self.LOG_NAME or self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(self.LOG_FORMAT)
        for handler in self.LOG_HANDLERS:
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)

        self.WATCH_EXCLUDE.extend(["%s/*" % self.BUILD_DIR, self.BUILD_DIR])
        self.WATCH_EXCLUDE = ["%s/%s" % (self.BASE_DIR, p) for p in self.WATCH_EXCLUDE]

        self.BUILD_DIR = path(self.BUILD_DIR)

        render.render.klass = self

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        for _command in command.register:
            sub_parser = subparsers.add_parser(
                _command.func.func_name,
                help=_command.func.__doc__
            )
            sub_parser.add_argument('args', nargs=argparse.REMAINDER)
            sub_parser.set_defaults(func=_command.func)

        args = parser.parse_args()
        args.func(self, args)

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

    def _clean_build_dir(self):
        if self.BUILD_DIR.exists:
            [element.rm(r=True) for element in self.BUILD_DIR]
        else:
            self.BUILD_DIR.mkdir()

    def _include(self):
        for element in self.INCLUDE:
            path(element).cp(self.BUILD_DIR / element)

    def _server(self):
        self._build()
        os.chdir(self.BUILD_DIR)

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        Handler.extensions_map[''] = 'text/html'

        def log_message(obj, format, *args):
            self.logger.info("%s %s" % ("serving", format % args))

        Handler.log_message = log_message
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        httpd = SocketServer.ThreadingTCPServer(
            ("", self.SERVER_PORT), Handler
        )

        self.logger.info("serving at port %s" % self.SERVER_PORT)
        httpd.serve_forever()

    def _build(self):
        self._clean_build_dir()
        self._include()

        for func in register.elements:
            for renderer in getattr(self, func)():
                self.write(renderer.name, renderer.content)

        self.logger.info('build generated')

    @command
    def build(self, args):
        self._build()

    @command
    def server(self, args):
        server = Process(target=self._server)
        server.start()

        event_handler = PatternMatchingEventHandler(ignore_patterns=self.WATCH_EXCLUDE)
        event_handler.on_modified = lambda event : self._build()
        observer = Observer()
        observer.schedule(event_handler, self.BASE_DIR, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            server.terminate()
            observer.stop()

        observer.join()

        self.logger.info("Clossing")
