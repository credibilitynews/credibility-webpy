import hashlib
import web
import db
import re

from pretty_date import pretty_date
from models import *





## routes
urls = (
  '/', 'index',

  '/login', 'login',
  '/register', 'register',
  '/logout', 'logout',
  '/user/(\d+)', 'user',
  
  # topic
  '/topic/new', 'new_topic',    
  '/topic/(\d+)', 'topic',
  '/topic/(\d+)/upvote', 'upvote_topic', # upvote story
  '/topic/(\d+)/base/new', 'new_base_link',  # add base story
  '/topic/(\d+)/alt/new',  'new_alt_link',  # add alt story
  
  # link
  '/link/(\d+)', 'link',  # add base story
  '/link/(\d+)/upvote', 'upvote_link',  # add base story
  '/link/(\d+)/view', 'view_link',  # add base story


  '/comment/(\d+)/upvote', 'upvote_comment',  # add base story

  '/about', 'about',
  '/faq', 'faq',
  '/contact', 'contact',

  '/favicon.ico','favicon'
)

def load_sqla(handler):
  try:
      return handler()
  except web.HTTPError:
     db.session.commit()
     raise
  except:
      db.session.rollback()
      raise
  finally:
      db.session.commit()
      # If the above alone doesn't work, uncomment 
      # the following line:
      #db.session.expunge_all() 

def shorten_link(link):
  l = re.findall(r"^https?://(.+)/?", link)

  if len(l) > 0:
    n=0
    try:
      n = l[0].index('/')
    except ValueError:
      n = len(l[0])

    return l[0][:n]
  else:
    return link

## app setup
app = web.application(urls, globals())
app.add_processor(load_sqla)

## session setup
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
    web.config._session = session
else:
    session = web.config._session





## favicon
class favicon:
  def GET(self):
    raise web.redirect('/static/favicon.ico')





## home page
class index:  
  def all_topics(self):
    return db.session.query(Topic).all()

  def GET(self):
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    username = None
    if hasattr(session,'username'):
      username = session.username
    
    topics = self.all_topics()
    topics = sorted(topics, key=lambda topic: topic.points, reverse=True)

    return render.index(topics)








## logout
class logout :
  def GET(self):
    session.kill()
    return web.seeother('/')


## login
class login:
  
  def valid_email_password(self, username, password):
    pwdhash = hashlib.md5(password).hexdigest()
    user = db.session.query(User).filter_by(name=username,password=pwdhash).first()
    if not user:
      return False
    else:
      session.user = user
      return True

  login_form = web.form.Form(
      web.form.Textbox('username', web.form.notnull, 
          size=30,
          description="username:"),
      web.form.Password('password', web.form.notnull,
          size=30,
          description="password:"),
      web.form.Button('login'),
  )

  def GET(self):
    session.kill()
    url = web.input(url='').url
    login_form = self.login_form()
    login_form.fill({'url':url})

    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.user.login(login_form, "Log in")

  def POST(self):
    i = web.input()
    login_form = self.login_form()
    login_success = self.valid_email_password(i.username, i.password)
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})

    if (not login_form.validates()) or (not login_success):
      return render.user.login(login_form, "Log in")
    else:
      session.logged_in = True
      session.username = session.user.name
      web.seeother('/')








## register
class register:
  def not_user_exists(username):
    user = db.session.query(User).filter_by(name=username).first()
    if not user:
      return True
    else:
      return False

  def not_email_exists(email):
    email = db.session.query(User).filter_by(email=email).first()
    if not email:
      return True
    else:
      return False

  user_exists_validator = web.form.Validator('Username already taken.', 
                                not_user_exists)


  vpass = web.form.regexp(r".{3,20}$", 'must be between 3 and 20 characters')
  vemail = web.form.regexp(r".*@.*", "must be a valid email address")

  registration_form = web.form.Form(
    web.form.Textbox('username', web.form.notnull, user_exists_validator,
        size=30,
        description="username:"),
    web.form.Password('password', web.form.notnull, vpass,
        size=30,
        description="password:", type="password"),
    web.form.Password("password2", web.form.notnull, vpass,
      description="repeat password:"),
    web.form.Button('sign up'),
    validators = [
        web.form.Validator("Passwords didn't match", lambda i: i.password == i.password2)]
  )


  def GET(self):
    url = web.input(url='').url

    registration_form = self.registration_form()
    registration_form.fill({'url':url})

    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.user.login(registration_form, "Sign up")


  def POST(self):
    i = web.input()

    registration_form = self.registration_form()
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})

    if not registration_form.validates():
      return render.user.login(registration_form, "Sign up")
    else:
      pwdhash = hashlib.md5(i.password).hexdigest()
      u = User(name=i.username
                ,password=pwdhash)
      db.session.add(u)
      db.session.commit()

      session.logged_in = True
      session.username = u.name
      session.user = u

      web.seeother('/')








## new topics
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

  title_exists_validator = web.form.Validator('Title already exists', 
                                not_title_exists)
  hashtag_exists_validator = web.form.Validator('Hashtag already exists', 
                                not_hashtag_exists)

  vhashtag = web.form.regexp(r"#.*", "must be a valid hashtag start with #")

  form = web.form.Form(
      web.form.Textbox('title', web.form.notnull, title_exists_validator,
          size=30,
          description="title:"),
      web.form.Textbox('hashtag', web.form.notnull, vhashtag, hashtag_exists_validator,
          size=30,
          placeholder="#topic_hashtag", 
          description="hashtag:"),
      web.form.Button('Create topic'),
  )

  def GET(self):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    url = web.input(url='').url
    form = self.form()
    form.fill({'url':url})

    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})


    return render.topic.new(form)

  def POST(self):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    i = web.input()

    form = self.form()
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})

    if not form.validates():
      return render.topic.new(form)
    else:
      topic = Topic(title=i.title, hashtag=i.hashtag, user_id=session.user.id)
      db.session.add(topic)
      topic.views = 0
      db.session.commit()

      web.seeother('/topic/%d' % topic.id)








## topic 
class topic:
  def topic(self, id):
    return db.session.query(Topic).filter_by(id=id).first()

  def GET(self, id):
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr, 'short': shorten_link, 'pretty_date': pretty_date })
    
    t = self.topic(id)
    db.session.query(Topic).filter_by(id=id).update({'views':t.views+1})

    return render.topic.show(id, self.topic(id))








## view link 
class view_link:
  def link(self, id):
    return db.session.query(Link).filter_by(id=id).first()

  def GET(self, id):
    l = self.link(id)
    db.session.query(Link).filter_by(id=id).update({'views':l.views+1})

    return web.seeother(l.url)








## upvote topic
class upvote_topic:
  def GET(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    voted = db.session.query(TopicVote).filter_by(topic_id=id, user_id=session.user.id).first()

    if not voted:
      vote = TopicVote(topic_id=id, user_id=session.user.id)
      db.session.add(vote)

    return web.seeother("/topic/%d" % int(id))







## new base link
class new_base_link:
  def not_link_exists(url):
    link = db.session.query(Link).filter_by(url=url).first()
    if not link:
      return True
    else:
      return False

  link_exists_validator = web.form.Validator('Link already exists', 
                                not_link_exists)

  vlink = web.form.regexp(r"https?://.+\..+", "must be a valid url start with http(s)")

  form = web.form.Form(
      web.form.Textbox('title', web.form.notnull, 
          size=30,
          description="title:"),
      web.form.Textbox('url', web.form.notnull, vlink, link_exists_validator,
          size=30,
          description="url:"),
      web.form.Button('add base story link'),
  )

  def GET(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    url = web.input(url='').url
    form = self.form()
    form.fill({'url':url})

    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.link.new(form, id)

  def POST(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    i = web.input()

    form = self.form()
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})

    if not form.validates():
      return render.link.new(form,id)
    else:
      link = Link(title=i.title, url=i.url, topic_id=id, user_id=session.user.id, type=1)
      db.session.add(link)
      db.session.commit()

      return web.seeother('/topic/%d' % int(id))







## new alternative story link
class new_alt_link:
  def not_link_exists(url):
    link = db.session.query(Link).filter_by(url=url).first()
    if not link:
      return True
    else:
      return False

  link_exists_validator = web.form.Validator('Link already exists', 
                                not_link_exists)
  vlink = web.form.regexp(r"https?://.+\..+", "must be a valid url start with http(s)")

  form = web.form.Form(
      web.form.Textbox('title', web.form.notnull, 
          size=30,
          description="title:"),
      web.form.Textbox('url', web.form.notnull, vlink, link_exists_validator,
          size=30,
          description="url:"),
      web.form.Button('add alternative story link'),
  )

  def GET(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    url = web.input(url='').url
    form = self.form()
    form.fill({'url':url})

    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.link.new(form,id)

  def POST(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    i = web.input()

    form = self.form()
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})

    if not form.validates():
      return render.link.new(form, id)
    else:
      link = Link(title=i.title, url=i.url, topic_id=id, user_id=session.user.id, type=2)
      db.session.add(link)
      db.session.commit()

      return web.seeother('/topic/%d' % int(id))






## link
class link:
  form = web.form.Form(
      web.form.Textarea('comment', web.form.notnull),
  )

  def link(self, id):
    return db.session.query(Link).filter_by(id=id).first()

  def GET(self, id):
    i = web.input()

    form = self.form()
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr, 'short': shorten_link, 'pretty_date':pretty_date})
    return render.link.show(form, id, self.link(id))

  def POST(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    i = web.input()

    form = self.form()
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr, 'short': shorten_link, 'pretty_date':pretty_date})

    if not form.validates():
      return render.link.show(form, id, self.link(id))
    else:
      comment = Comment(content=i.comment, link_id=id, user_id=session.user.id)
      db.session.add(comment)
      db.session.commit()

      return web.seeother('/link/%d' % int(id))







## upvote link
class upvote_link:
  def GET(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    voted = db.session.query(LinkVote).filter_by(link_id=id, user_id=session.user.id).first()

    if not voted:
      vote = LinkVote(link_id=id, user_id=session.user.id)
      db.session.add(vote)

    return web.seeother("/link/%d" % int(id))






## upvote comment
class upvote_comment:
  def GET(self, id):
    username = None
    if hasattr(session, 'username'):
      username = session.username
    else:
      return web.seeother('/register')

    voted = db.session.query(CommentVote).filter_by(comment_id=id, user_id=session.user.id).first()

    if not voted:
      vote = CommentVote(comment_id=id, user_id=session.user.id)
      db.session.add(vote)

    comment = db.session.query(Comment).filter_by(id=id).first()

    return web.seeother("/link/%d" % int(comment.link_id))





## user
class user:
  def GET(self,id):
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.user.show(id)




## static pages
class about:
  def GET(self):
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.static.about()

class faq:
  def GET(self):
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.static.faq()

class contact:
  def GET(self):
    render = web.template.render('templates/', base='layout', globals={'session':session, 'hasattr':hasattr,'pretty_date':pretty_date})
    return render.static.contact()





if __name__ == "__main__":
    app.run()