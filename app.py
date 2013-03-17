import hashlib
import web
import db

from models import *

urls = (
  '/', 'index',

  '/login', 'login',
  '/register', 'register',
  '/logout', 'logout',
  '/user/(\d+)', 'user',
  
  # topic
  '/topic/new', 'new_topic',    
  '/topic/upvote', 'topic', # upvote story
  '/topic/(\d+)', 'topic',
  '/topic/(\d+)/base/new', 'new_base_link',  # add base story
  '/topic/(\d+)/alt/new',  'new_alt_link',  # add alt story
  
  # link
  '/link/(\d+)', 'link',  # add base story
  '/link/(\d+)/upvote', 'link',  # add base story
  # comment
  '/link/(\d+)/comment', 'new_comment',


  '/about', 'about',
  '/faq', 'faq',
  '/contact', 'contact'

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

app = web.application(urls, globals())
app.add_processor(load_sqla)

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
    web.config._session = session
else:
    session = web.config._session





## home page
class index:        
  def GET(self):
    render = web.template.render('templates/', base='layout')
    username = False
    if hasattr(session,'username'):
      username = session.username
    else:
      username = False
    web.debug(username)
    return render.index(username)





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
    url = web.input(url='').url
    login_form = self.login_form()
    login_form.fill({'url':url})

    render = web.template.render('templates/', base="layout")
    return render.user.login(login_form, "Log in")

  def POST(self):
    i = web.input()
    login_form = self.login_form()
    login_success = self.valid_email_password(i.username, i.password)
    render = web.template.render('templates/', base="layout")

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

  email_exists_validator = web.form.Validator('Email already registered.', 
                                not_email_exists)

  vpass = web.form.regexp(r".{3,20}$", 'must be between 3 and 20 characters')
  vemail = web.form.regexp(r".*@.*", "must be a valid email address")

  registration_form = web.form.Form(
    web.form.Textbox('username', web.form.notnull, user_exists_validator,
        size=30,
        description="username:"),
    web.form.Textbox('email', web.form.notnull, vemail, email_exists_validator,
        size=30,
        description="email:"),
    web.form.Password('password', web.form.notnull, vpass,
        size=30,
        description="password:", type="password"),
    web.form.Password("password2", web.form.notnull, vpass,
      description="repeat password:"),
    web.form.Button('sign up'),
    validators = [
        web.form.Validator("Passwords did'nt match", lambda i: i.password == i.password2)]
  )


  def GET(self):
    url = web.input(url='').url

    registration_form = self.registration_form()
    registration_form.fill({'url':url})

    render = web.template.render('templates/', base="layout")
    return render.user.login(registration_form, "Sign up")


  def POST(self):
    i = web.input()

    registration_form = self.registration_form()
    render = web.template.render('templates/', base="layout")

    if not registration_form.validates():
      return render.user.login(registration_form, "Sign up")
    else:
      pwdhash = hashlib.md5(i.password).hexdigest()
      u = User(name=i.username
                ,email=i.email
                ,password=pwdhash)
      db.session.add(u)
      db.session.commit()

      session.logged_in = True
      session.username = u.name

      web.seeother('/')







## new topics
class new_topic:
  def not_page_exists(url):
    return True

  topic_exists_validator = web.form.Validator('Page already exists', 
                                not_page_exists)

  form = web.form.Form(
      web.form.Textbox('title', web.form.notnull, topic_exists_validator,
          size=30,
          description="title:"),
      web.form.Textbox('hashtag', web.form.notnull, 
          size=30,
          placeholder="#something",
          description="hashtag:"),
      web.form.Button('Create topic'),
  )

  def GET(self):
    url = web.input(url='').url
    form = self.form()
    form.fill({'url':url})

    render = web.template.render('templates/', base='layout')
    return render.topic.new(form)



## topic 
class topic:
  def GET(self, id):
    render = web.template.render('templates/', base='layout')
    return render.topic.show(id)



## new base link
class new_base_link:
  def not_link_exists(url):
    return True

  link_exists_validator = web.form.Validator('Page already exists', 
                                not_link_exists)

  form = web.form.Form(
      web.form.Textbox('title', web.form.notnull, link_exists_validator,
          size=30,
          description="title:"),
      web.form.Textbox('url', web.form.notnull,
          size=30,
          description="url:"),
      web.form.Button('add base story link'),
  )

  def GET(self, id):
    url = web.input(url='').url
    form = self.form()
    form.fill({'url':url})

    render = web.template.render('templates/', base='layout')
    return render.link.new(form, id)



## new alternate link
class new_alt_link:
  def not_link_exists(url):
    return True

  link_exists_validator = web.form.Validator('Page already exists', 
                                not_link_exists)

  form = web.form.Form(
      web.form.Textbox('title', web.form.notnull, link_exists_validator,
          size=30,
          description="title:"),
      web.form.Textbox('url', web.form.notnull,
          size=30,
          description="url:"),
      web.form.Button('add alternate story link'),
  )

  def GET(self, id):
    url = web.input(url='').url
    form = self.form()
    form.fill({'url':url})

    render = web.template.render('templates/', base='layout')
    return render.link.new(form,id)




## link
class link:
  def GET(self, id):
    render = web.template.render('templates/', base='layout')
    return render.link.show(id)



## new_comment
class new_comment:
  def POST(self, id):
    return web.seeother("/link/id")



## user
class user:
  def GET(self,id):
    render = web.template.render('templates/', base='layout')
    return render.user.show(id)



## static pages
class about:
  def GET(self):
    render = web.template.render('templates/', base='layout')
    return render.static.about()

class faq:
  def GET(self):
    render = web.template.render('templates/', base='layout')
    return render.static.faq()

class contact:
  def GET(self):
    render = web.template.render('templates/', base='layout')
    return render.static.contact()

if __name__ == "__main__":
    app.run()