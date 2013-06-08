from osome import path
from jinja2 import Environment, FileSystemLoader


class render(object):
    pass


class content(render):
    """
    Renderer class to create a file from a content. Use **name** as a name for destination file.
    Create **content** to fill the file in.
    """

    def __init__(self, name, content):
        self.name = name
        self.content = content


class template(content):
    """
    Renderer class to render file from a template. Use **name** as a name for destination file.
    **template** for source jinja2 template located in the template directory,
    use some **context** for fill template in.
    """

    def __init__(self, name, template, **context):
        self.name = name
        self.content = self.template(template).render(**context)

    def template(self, template_name):
        env = Environment(loader=FileSystemLoader(self.klass.TEMPLATES_DIR))
        return env.get_template(path(template_name))

