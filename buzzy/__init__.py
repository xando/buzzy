import os
import sys
import re
import time
import codecs
import argparse
import markdown
import SimpleHTTPServer
import SocketServer

from osome import path
from datetime import datetime
from pygments.formatters import HtmlFormatter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from multiprocessing import Process


class WatchCode(FileSystemEventHandler):
    def on_modified(self, event):
        if not re.match('^.*/build/.*$', event.src_path):
            BaseBlog().build()


class BaseBlog(object):

    BASE_DIR = path(os.getcwd())
    BUILD_DIRECTORY = BASE_DIR / 'build'
    POSTS_DIR = BASE_DIR / 'posts'
    INDEX = BASE_DIR / 'index.html'
    EXTRA = [BASE_DIR / 'libs', BASE_DIR / 'img']
    PYGMENTS_STYLE = "emacs"
    SERVER_PORT = 8000

    read = lambda self,n: codecs.open(n, encoding='utf-8').read()
    write = lambda self,n,c: codecs.open(n, encoding='utf-8', mode="w").write(c)

    def __new__(self, *args, **kwargs):
        try:
            sys.path.append(self.BASE_DIR)
            from blog import Blog
            return super(BaseBlog, self).__new__(Blog, *args, **kwargs)
        except ImportError:
            return super(BaseBlog, self).__new__(BaseBlog, *args, **kwargs)

    def _watch(self):
        observer = Observer()
        observer.schedule(WatchCode(), path=self.BASE_DIR, recursive=True)
        observer.start()

        while True:
            time.sleep(1)

    def _server(self):
        os.chdir(self.BUILD_DIRECTORY)

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        httpd = SocketServer.ThreadingTCPServer(("", self.SERVER_PORT), Handler)

        print "serving at port %s" % self.SERVER_PORT
        httpd.serve_forever()

    def server(self):
        self.build()

        watch = Process(target=self._watch)
        watch.start()
        server = Process(target=self._server)
        server.start()

        try:
            watch.join()
            server.join()
        except KeyboardInterrupt:
            watch.terminate()
            server.terminate()

    def render_index(_file):
        pass
    def build(self):
        POSTS = list(path(self.POSTS_DIR).walk(pattern='*.md', r=True))

        if self.BUILD_DIRECTORY.exists:
            [element.rm(r=True) for element in self.BUILD_DIRECTORY]
        else:
            self.BUILD_DIRECTORY.mkdir()

        for extra in self.EXTRA:
            extra.cp(self.BUILD_DIRECTORY / extra.basename, r=True)

        index_content = self.read(self.INDEX)

        RESULTS = []
        for post in POSTS:
            name = post.basename.split('.')[0]
            generated_name = path("%s.html" % name)

            markdown_content = codecs.open(post, encoding='utf-8').read()
            md = markdown.Markdown(extensions=['codehilite', 'meta'])
            html_content = md.convert(markdown_content)

            self.write(
                self.BUILD_DIRECTORY / generated_name,
                index_content % html_content
            )

            RESULTS.append(
                {"title": md.Meta['title'][0], "link": generated_name}
            )

        index_main = "".join([
            '<a href="%(link)s"><h1>%(title)s</h1></a><div class="break">...</div>' % e
            for e in RESULTS
        ])

        self.write(
            self.BUILD_DIRECTORY / 'index.html',
            index_content % index_main
        )
        self.write(
            self.BUILD_DIRECTORY / 'libs' / 'pygments.css',
            HtmlFormatter(style=self.PYGMENTS_STYLE).get_style_defs()
        )

        print "Generated %s" % datetime.now()


def server(args):
    BaseBlog().server()


def build(args):
    BaseBlog().build()


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
