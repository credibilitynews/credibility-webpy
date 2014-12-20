import web
from web import ctx
import json

import db
from tools import shorten_link, pretty_date
from models.tag import Tag
from models.topic import Topic, TopicVote

urls = (
    '/new', 'new_topic',
    '/latest', 'latest',

    '/(\d+)', 'topic',
    '/(\d+)/upvote', 'upvote_topic',
    '/(\d+)/left/new', 'new_left_link',
    '/(\d+)/right/new', 'new_right_link',
    '/(\d+)/fact/new', 'new_fact_link')

app = web.application(urls, locals())


class new_topic:
    def not_title_exists(title):
        topic = db.session.query(Topic).filter_by(title=title).first()
        if not topic:
            return True
        else:
            return False

    def not_hashtag_exists(hashtag):
        topic = db.session.query(Topic).filter_by(hashtag=hashtag).first()
        if not topic:
            return True
        else:
            return False

    def all_tags(self=None):
        return sorted(
            db.session.query(Tag).all(),
            cmp=lambda x, y: cmp(x.name, y.name))

    title_exists_validator = web.form.Validator(
        'Title already exists', not_title_exists)
    hashtag_exists_validator = web.form.Validator(
        'Hashtag already exists', not_hashtag_exists)

    vhashtag = web.form.regexp(r"#.*", "must be a valid hashtag start with #")

    form = web.form.Form(
        web.form.Textbox(
            'title', web.form.notnull, title_exists_validator,
            size=30, description="title:"),
        web.form.Textbox(
            'hashtag', web.form.notnull, vhashtag, hashtag_exists_validator,
            size=30,
            placeholder="#topic_hashtag",
            description="hashtag:"),
        web.form.Dropdown(
            'tag', map(lambda tag: (tag.id, tag.name), all_tags()),
            description="main category:"),
        web.form.Button('Create topic'),
    )

    def GET(self):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        url = web.input(url='').url
        form = self.form()
        form.fill({'url': url})

        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})

        return render.topic.new(form)

    def POST(self):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        i = web.input()

        form = self.form()
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})

        if not form.validates():
            return render.topic.new(form)
        else:
            topic = Topic(
                title=i.title, hashtag=i.hashtag,
                user_id=ctx.session.user.id)
            topic.views = 1
            tag = db.session.query(Tag).get(i.tag)
            topic.tags.append(tag)
            db.session.add(topic)
            db.session.commit()

            web.seeother('/topic/%d' % topic.id, absolute=True)


class topic:
    def topic(self, id):
        return db.session.query(Topic).filter_by(id=id).first()

    def GET(self, id):
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'short': shorten_link, 'pretty_date': pretty_date})

        t = self.topic(id)
        db.session.query(Topic).filter_by(id=id).update({'views': t.views+1})
        
        web.header("Access-Control-Allow-Origin", "http://localhost:8000")
        web.header("Access-Control-Allow-Credentials", 'true')
        web.header("Content-Type", 'application/json')
        return json.dumps({
            "data": self.topic(id).serialize
        })


class upvote_topic:
    def GET(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        voted = db.session.query(TopicVote).filter_by(
            topic_id=id, user_id=ctx.session.user.id).first()

        if not voted:
            vote = TopicVote(topic_id=id, user_id=ctx.session.user.id)
            db.session.add(vote)

        return web.seeother("/topic/%d" % int(id), absolute=True)


class new_left_link:
    def not_link_exists(url):
        link = db.session.query(Link).filter_by(url=url).first()
        if not link:
            return True
        else:
            return False

    link_exists_validator = web.form.Validator(
        'Link already exists', not_link_exists)

    vlink = web.form.regexp(
        r"https?://.+\..+", "must be a valid url start with http(s)")

    form = web.form.Form(
        web.form.Textbox(
            'title', web.form.notnull,
            size=30,
            description="title:",
            **{'ng-model': "title"}),
        web.form.Textbox(
            'url', web.form.notnull, vlink, link_exists_validator,
            size=30,
            description="url:",
            **{'ng-model': 'url', 'ng-change': "suggestTitle()"}),
        web.form.Button('add story link'),
    )

    def GET(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        url = web.input(url='').url
        form = self.form()
        form.fill({'url': url})
        path = '/topic/'+id+'/left/new'
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})
        return render.link.new(form, id, path)

    def POST(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        i = web.input()

        form = self.form()
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})

        if not form.validates():
            path = '/topic/'+id+'/left/new'
            return render.link.new(form, id, path)
        else:
            link = Link(
                title=i.title, url=i.url,
                topic_id=id, user_id=ctx.session.user.id, type=1)
            link.views = 1
            db.session.add(link)
            db.session.commit()

            return web.seeother('/topic/%d' % int(id), absolute=True)


class new_fact_link:
    def not_link_exists(url):
        link = db.session.query(Link).filter_by(url=url).first()
        if not link:
            return True
        else:
            return False

    link_exists_validator = web.form.Validator(
        'Link already exists', not_link_exists)
    vlink = web.form.regexp(
        r"https?://.+\..+", "must be a valid url start with http(s)")

    form = web.form.Form(
        web.form.Textbox(
            'title', web.form.notnull,
            size=30,
            description="title:",
            **{'ng-model': "title"}),
        web.form.Textbox(
            'url', web.form.notnull, vlink, link_exists_validator,
            size=30,
            description="url:",
            **{'ng-model': 'url', 'ng-change': "suggestTitle()"}),
        web.form.Button('add fact-based news link'),
    )

    def GET(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        url = web.input(url='').url
        form = self.form()
        form.fill({'url': url})
        path = '/topic/' + id + '/fact/new'

        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})
        return render.link.new(form, id, path)

    def POST(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        i = web.input()

        form = self.form()
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})

        if not form.validates():
            path = '/topic/'+id+'/fact/new'
            return render.link.new(form, id, path)
        else:
            link = Link(
                title=i.title, url=i.url,
                topic_id=id, user_id=ctx.session.user.id, type=0)
            link.views = 1
            db.session.add(link)
            db.session.commit()

            return web.seeother('/topic/%d' % int(id), absolute=True)


class new_right_link:
    def not_link_exists(url):
        link = db.session.query(Link).filter_by(url=url).first()
        if not link:
            return True
        else:
            return False

    link_exists_validator = web.form.Validator(
        'Link already exists', not_link_exists)
    vlink = web.form.regexp(
        r"https?://.+\..+", "must be a valid url start with http(s)")

    form = web.form.Form(
        web.form.Textbox(
            'title', web.form.notnull,
            size=30,
            description="title:",
            **{'ng-model': "title"}),
        web.form.Textbox(
            'url', web.form.notnull, vlink, link_exists_validator,
            size=30,
            description="url:",
            **{'ng-model': 'url', 'ng-change': "suggestTitle()"}),
        web.form.Button('add story link'),
    )

    def GET(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        url = web.input(url='').url
        form = self.form()
        form.fill({'url': url})
        path = '/topic/'+id+'/right/new'
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})
        return render.link.new(form, id, path)

    def POST(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        i = web.input()

        form = self.form()
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})

        if not form.validates():
            path = '/topic/'+id+'/right/new'
            return render.link.new(form, id, path)
        else:
            link = Link(
                title=i.title, url=i.url,
                topic_id=id, user_id=ctx.session.user.id, type=2)
            link.views = 1
            db.session.add(link)
            db.session.commit()

            return web.seeother('/topic/%d' % int(id), absolute=True)
