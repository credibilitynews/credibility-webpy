import web
from web import ctx

import db
from tools import shorten_link, pretty_date
from models.tag import Tag

urls = ('/(.+)', 'tag')

app = web.application(urls, globals())


class tag:
    def tag(self, code):
        return db.session.query(Tag).filter_by(code=code).first()

    def all_tags(self):
        return sorted(
            db.session.query(Tag).all(),
            key=lambda x: x.name)

    def child_topics(self, child):
        topics = child.topics[:]
        return topics

    def GET(self, code):
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'short': shorten_link, 'pretty_date': pretty_date})
        tags = self.all_tags()
        tag = self.tag(code)
        topics = tag.topics[:]
        if len(tag.children) > 0:
            child_topics = map(self.child_topics, tag.children)
            child_topics = reduce(lambda x, y: x+y, child_topics)
            topics = sorted(
                topics + child_topics,
                key=lambda topic: topic.points, reverse=True)
        return render.tag.show(id, tags, tag, topics)
