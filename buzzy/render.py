from osome import path
from jinja2 import Environment, FileSystemLoader

from buzzy.packages import markdown as _markdown


class render(object):
    pass


class content(render):

    def __init__(self, name, content):
        self.name = name
        self.content = content


class template(content):

    def __init__(self, name, template, **context):
        self.name = name
        self.content = self.template(template).render(**context)

    def template(self, template_name):
        env = Environment(loader=FileSystemLoader(self.klass.TEMPLATES_DIR))
        return env.get_template(path(template_name))


class markdown(content):

    def __init__(self, name, source):
        md = _markdown.Markdown(extensions=[
            'buzzy.packages.markdown.extensions.codehilite',
            'buzzy.packages.markdown.extensions.meta'
        ])
        self.name = name
        self.content = md.convert(path(source).content)
        self.meta = {a:b if len(b) > 1 else b[0] for a,b in md.Meta.items()}