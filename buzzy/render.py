import codecs
from functools import partial

from osome import path


register = []

class render(object):

    def __init__(self, func):
        register.append(func.func_name)
        self.func = func

    def __call__(self, *args, **kwargs):
        value = self.func(*args, **kwargs)
        if not isinstance(value, list):
            value = [value]

        return self.render(value)

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)

    def write(self, name, content):
        codecs.open(name, encoding='utf-8', mode="w").write(content)


class copy(render):
    def render(self, value):
        for v in value:
            path(v).cp(path(self.klass.BUILD_DIR) / v, r=True)


class content(render):

    def ensure_path(self, name):
        directory = path(name).dir()
        directory_build = path(self.klass.BUILD_DIR) / directory
        if directory and not directory_build.exists:
            directory_build.mkdir(p=True)

    def render(self, value):

        for name, content in value:
            self.ensure_path(name)
            self.write(path(self.klass.BUILD_DIR) / name, content)


class template(content):

    def render(self, value):

        for name, template, context in value:
            self.ensure_path(name)
            content = self.klass.template(template).render(**context)
            self.write(path(self.klass.BUILD_DIR) / name, content)
