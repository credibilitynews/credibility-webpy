import hashlib
import web
import db
import os

from controllers import page, topic, feed, link, tagged, user

urls = (
    '/feed', feed.feed,
    '/topic', topic.app,
    '/link', link.app,
    '/tagged', tagged.app,
    '/user', user.app,

    '/favicon.ico', page.favicon,
    '/about', page.about,
    '/contact', page.contact,
    '/faq', page.faq,
    '/latest', page.latest,

    '/', page.index
)


app = web.subdir_application(urls)
# session = web.session.Session(app, web.session.DiskStore('sessions'))


def session_hook():
    web.ctx.session = {}  # session


app.add_processor(web.loadhook(session_hook))
app.add_processor(db.load_sqla)

if __name__ == "__main__":
    app.run()
