import web
import json
import requests
from web import ctx

from bs4 import BeautifulSoup

import db
from tools import shorten_link, pretty_date
from models.comment import Comment, CommentVote
from models.link import Link, LinkVote

urls = (
    '/suggest/title', 'suggest_title',
    '/(\d+)', 'link',
    '/(\d+)/upvote', 'upvote_link',
    '/(\d+)/view', 'view_link')

app = web.application(urls, globals())


class suggest_title:

    def _title_from_url(self, url):
        try:
            page = requests.get(url, verify=True)
            text = page.content
            return BeautifulSoup(text).title.string.strip()
        except:
            return ''

    def GET(self):
        data = web.input()
        if 'url' not in data:
            return json.dumps({'error': 'url param is missing'})
        else:
            title = self._title_from_url(data['url'])
            return json.dumps({'title': title.encode('utf-8')})


class view_link:

    def _link(self, id):
        return db.session.query(Link).filter_by(id=id).first()

    def GET(self, id):
        l = self._link(id)
        db.session.query(Link).filter_by(id=id).update({'views': l.views + 1})
        db.session.commit()

        return web.seeother(l.url, absolute=True)


class link:
    form = web.form.Form(
        web.form.Textarea('comment', web.form.notnull),
    )

    def link(self, id):
        return db.session.query(Link).filter_by(id=id).first()

    def GET(self, id):
        i = web.input()

        form = self.form()
        render = web.template.render(
            'templates/',
            base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'short': shorten_link, 'pretty_date': pretty_date})
        return render.link.show(form, id, self.link(id))

    def POST(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        i = web.input()

        form = self.form()
        render = web.template.render(
            'templates/',
            base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'short': shorten_link, 'pretty_date': pretty_date})

        if not form.validates():
            return render.link.show(form, id, self.link(id))
        else:
            comment = Comment(
                content=i.comment, link_id=id, user_id=ctx.session.user.id)
            db.session.add(comment)
            db.session.commit()

            return web.seeother('/link/%d' % int(id), absolute=True)


class upvote_link:
    def GET(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        voted = db.session.query(LinkVote).filter_by(
            link_id=id, user_id=ctx.session.user.id).first()

        if not voted:
            vote = LinkVote(link_id=id, user_id=ctx.session.user.id)
            db.session.add(vote)

        return web.seeother("/link/%d" % int(id), absolute=True)
