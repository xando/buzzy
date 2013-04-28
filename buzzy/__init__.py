import argparse
import os
import codecs
import markdown
import SimpleHTTPServer
import SocketServer

from osome import path
from datetime import datetime
from pygments.formatters import HtmlFormatter

BASE_DIR = path(os.getcwd())


def server(args):
    os.chdir('build')
    PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "serving at port", PORT
    httpd.serve_forever()


def create(args):
    blog_dir = (BASE_DIR / args.name).mkdir()
    package_dir = path(__file__).dir()

    (package_dir / 'index.html').cp(blog_dir / 'index.html')
    (package_dir / 'libs').cp(blog_dir / 'libs', r=True)
    (package_dir / 'posts').cp(blog_dir / 'posts', r=True)
    (package_dir / 'img').cp(blog_dir / 'img', r=True)


def build(args):

    BUILD_DIRECTORY = BASE_DIR / 'build'
    POSTS_DIR = BASE_DIR / 'posts'
    INDEX = BASE_DIR / 'index.html'

    POSTS = list(path(POSTS_DIR).walk(pattern='*.md', r=True))

    EXTRA = [
        BASE_DIR / 'libs',
        BASE_DIR / 'img',
    ]

    PYGMENTS_STYLE = "emacs"

    if BUILD_DIRECTORY.exists:
        [element.rm(r=True) for element in BUILD_DIRECTORY]
    else:
        BUILD_DIRECTORY.mkdir()

    for extra in EXTRA:
        extra.cp(BUILD_DIRECTORY / extra.basename, r=True)

    index_content = codecs.open(INDEX,  encoding='utf-8').read()

    RESULTS = []
    for post in POSTS:
        name = post.basename.split('.')[0]
        generated_name = path("%s.html" % name)

        markdown_content = codecs.open(post, encoding='utf-8').read()
        md = markdown.Markdown(extensions=['codehilite', 'meta'])
        html_content = md.convert(markdown_content)

        codecs.open(BUILD_DIRECTORY / generated_name, encoding='utf-8', mode="w").write(
            index_content % html_content
        )

        RESULTS.append(
            {"title": md.Meta['title'][0], "link": generated_name}
        )

    index_main = "".join([
        '<a href="%(link)s"><h1>%(title)s</h1></a><div class="break">...</div>' % e
        for e in RESULTS
    ])

    codecs.open(BUILD_DIRECTORY / 'index.html', encoding='utf-8', mode="w").write(
        index_content % index_main
    )

    (BUILD_DIRECTORY / 'libs' / 'pygments.css').open('w').write(
        HtmlFormatter(style=PYGMENTS_STYLE).get_style_defs()
    )
    print "Generated %s" % datetime.now()


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
