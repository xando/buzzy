import buzzy


class StaticSite(buzzy.Base):

    @buzzy.render
    def index(self):
        return "index.html", "test"