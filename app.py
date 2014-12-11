import hashlib
import web
import db

from controllers import page, topic, feed, link, tagged, user

urls = (
    '/v1/feed', feed.feed,
    '/v1/topic', topic.app,
    '/v1/link', link.app,
    '/v1/categories', tagged.app,
    '/v1/user', user.app,

    '/favicon.ico', page.favicon,
    '/v1/about', page.about,
    '/v1/contact', page.contact,
    '/v1/faq', page.faq,
    '/v1/latest', page.latest,

    '/v1/home', page.index
)

app = web.subdir_application(urls)


def session_hook():
    session = web.session.Session(app, web.session.DiskStore('sessions'))
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))
app.add_processor(db.load_sqla)


from livereload import Server, shell
if __name__ == "__main__":
    wsgiapp = app.wsgifunc()
    server = Server(wsgiapp)
    server.watch("*.py", "chrome-cli reload -t 63")
    server.serve(port=8080, host='localhost')
    #app.run()
