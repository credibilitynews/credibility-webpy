import hashlib
import web
import db
import os
from urlparse import urlparse

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

url = urlparse(os.environ['DATABASE_URL'])
dbs = web.database(dbn='postgres', db=url.path[1:], host=url.hostname, port=url.port, user=url.username, pw=url.password)
store = web.session.DBStore(dbs, 'user_sessions')
session = web.session.Session(app, store, initializer={'count': 0})

def session_hook():
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))
app.add_processor(db.load_sqla)

if __name__ == "__main__":
    app.run()
