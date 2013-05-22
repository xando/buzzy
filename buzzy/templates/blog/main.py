import buzzy


class StaticSite(buzzy.Base):

    @buzzy.render
    def index(self):

        return "index.html", self.render_template('index.html',
            title="The Blog",
            author="My name",
            posts_list=buzzy.path('posts')
        )