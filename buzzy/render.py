import sys
from buzzy.path import path


class render(object):
    pass


class content(render):

    def __init__(self, name, content):
        self.name = name
        self.content = content


class template(content):

    def __init__(self, template_file, name,  **context):

        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError:
            self.klass.logger.error("Python jinja2 package is required")
            sys.exit()

        env = Environment(loader=FileSystemLoader(self.klass.TEMPLATES_DIR))
        template = env.get_template(path(template_file))

        self.name = name
        self.content = template.render(**context)


class markdown(content):

    def __init__(self, source, name):

        try:
            import markdown
        except ImportError:
            self.klass.logger.error("Python markdown package is required")
            sys.exit()

        md = markdown.Markdown(extensions=['codehilite', 'meta'])

        self.name = name
        self.content = md.convert(path(source).content)
        self.meta = {a:b if len(b) > 1 else b[0] for a,b in md.Meta.items()}