import os
import webob.exc
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from fiber.route import Route

class Fiber(object):
    __handler = None # name mungling -> _Fiber__handler
    
    def __init__(self, route):
        self.__route = Route(route, os.environ)
        
    def __call__(self, action):
        if self.__handler is not None: return action
        if self.__route.match():
            self.__action = lambda: action(self, **self.__route.path_params())
            self.__class__.__handler = self
        return action
        
    @classmethod
    def run(cls):
        if cls.__handler is not None:
            def wsgi_app(env, start_response):
                cls.__handler.request = webapp.Request(env)
                cls.__handler.response = webapp.Response()
                result = cls.__handler.__action()
                cls.__handler.response.wsgi_write(start_response)
                return [result or '']
            run_wsgi_app(wsgi_app)
        else:
            run_wsgi_app(webob.exc.HTTPNotFound('Error 404'))
        pass