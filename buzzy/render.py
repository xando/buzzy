import codecs

from osome import path

class render(object):

    def ensure_path(self, name):
        directory = path(name).dir()
        directory_build = path(self.klass.BUILD_DIR) / directory
        if directory and not directory_build.exists:
            directory_build.mkdir(p=True)

    def write(self, name, content):
        codecs.open(name, encoding='utf-8', mode="w").write(content)


class copy(render):
    def __init__(self, *args):
        for value in args:
            path(value).cp(path(self.klass.BUILD_DIR) / value, r=True)


class content(render):

    def __init__(self, name, content):
        self.ensure_path(name)
        self.write(path(self.klass.BUILD_DIR) / name, content)


class template(content):

    def __init__(self, name, template, **context):
        self.ensure_path(name)
        content = self.klass.template(template).render(**context)
        self.write(path(self.klass.BUILD_DIR) / name, content)
