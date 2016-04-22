import json
import os

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def todo_key(id_key):
    return ndb.Key('AuthorTodo', id_key)


class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Todo(ndb.Model):
    author = ndb.StructuredProperty(Author)
    text = ndb.StringProperty(indexed=False)
    done = ndb.BooleanProperty(default=False, indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class ApiHandler(webapp2.RequestHandler):
    def _process_todos(self, todo):
        data = todo.to_dict(exclude=['date', 'author'])
        data['id'] = todo.key.id()
        return data

    def dispatch(self):
        self.cur_user = users.get_current_user()
        result = super(ApiHandler, self).dispatch()
        return result

    def post(self):
        data = json.loads(self.request.body)

        todo = Todo(parent=todo_key(self.cur_user.user_id()))
        todo.text = data.get('text', '')
        todo.author = Author(identity=users.get_current_user().user_id(), email=users.get_current_user().email())
        key = todo.put()
        data = todo.to_dict(exclude=['date', 'author'])
        data['id'] = key.id()
        data = json.dumps(data)
        self.response.write(data)

    def delete(self, pk):
        todo = Todo.get_by_id(int(pk), parent=todo_key(self.cur_user.user_id()))
        todo.key.delete()

    def patch(self, pk):
        todo = Todo.get_by_id(int(pk), parent=todo_key(self.cur_user.user_id()))
        data = json.loads(self.request.body)
        todo.done = data['done']
        todo.put()

        data = todo.to_dict(exclude=['date', 'author'])
        data['id'] = todo.key.id()
        data = json.dumps(data)
        self.response.write(data)

    def get(self):
        todo_query = Todo.query(ancestor=todo_key(self.cur_user.user_id())).order(Todo.date)
        todos = todo_query.fetch()
        data = map(self._process_todos, todos)
        self.response.write(json.dumps(data))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/api/todo/', ApiHandler),
    ('/api/todo/(\d+)/', ApiHandler),
], debug=True)
# [END app]
