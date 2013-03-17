import web
import db

from sqlalchemy.orm import scoped_session, sessionmaker
from models import user
import db

urls = (
  '/', 'index',

  '/login', 'login',
  '/logout', 'login',
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
    web.ctx.orm = scoped_session(sessionmaker(bind=db.engine))
    try:
        return handler()
    except web.HTTPError:
       web.ctx.orm.commit()
       raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
        # If the above alone doesn't work, uncomment 
        # the following line:
        #web.ctx.orm.expunge_all() 

app = web.application(urls, globals())
app.add_processor(load_sqla)


## home page
class index:        
  def GET(self):
    render = web.template.render('templates/', base='layout')
    name = 'alvinsj'
    return render.index(name)


## login
class login:
  def not_user_exists(url):
    return True

  user_exists_validator = web.form.Validator('Page already exists', 
                                not_user_exists)

  vpass = web.form.regexp(r".{3,20}$", 'must be between 3 and 20 characters')
  vemail = web.form.regexp(r".*@.*", "must be a valid email address")
  
  registration_form = web.form.Form(
      web.form.Textbox('username', web.form.notnull, user_exists_validator,
          size=30,
          description="username:"),
      web.form.Textbox('email', web.form.notnull, vemail,
          size=30,
          description="email:"),
      web.form.Textbox('password', web.form.notnull, vpass,
          size=30,
          description="password:"),
      web.form.Button('sign up'),
  )

  login_form = web.form.Form(
      web.form.Textbox('username', web.form.notnull,
          size=30,
          description="username:"),
      web.form.Textbox('password', web.form.notnull, vpass,
          size=30,
          description="password:"),
      web.form.Button('login'),
  )

  def GET(self):
    url = web.input(url='').url
    login_form = self.login_form()
    login_form.fill({'url':url})

    registration_form = self.registration_form()
    registration_form.fill({'url':url})

    render = web.template.render('templates/', base="layout")
    return render.user.login(login_form, registration_form)

  def POST(self):
    login_form = self.login_form()
    registration_form = self.registration_form()

    render = web.template.render('templates/', base="layout")

    if not registration_form.validates():
      return render.user.login(login_form, registration_form)
    else:
      web.seeother('/')
        # do whatever is required for registration



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