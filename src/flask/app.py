# This file is part of the Flask project and is copyrighted by the Flask authors.
# It is being used here for demonstration purposes.
# Original source: https://github.com/pallets/flask

from .globals import request_ctx
from .helpers import _endpoint_from_view_func
from .signals import request_started, request_finished
from .wrappers import Request


class App:
    """Base class for Flask applications."""
    
    def __init__(self, name):
        self.name = name
        self.view_functions = {}
        self.url_map = None
        
    def route(self, rule, **options):
        """Decorator to register a view function for a given URL rule."""
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator
    
    def add_url_rule(self, rule, endpoint, view_func, **options):
        """Register a URL rule."""
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        self.view_functions[endpoint] = view_func
        
    def wsgi_app(self, environ, start_response):
        """WSGI application interface."""
        ctx = self.request_context(environ)
        request_started.send(self)
        try:
            response = self.full_dispatch_request()
        except Exception as e:
            response = self.handle_exception(e)
        return response(environ, start_response)
    
    def request_context(self, environ):
        """Create a request context."""
        return request_ctx(self, environ)
    
    def full_dispatch_request(self):
        """Dispatch the request to the view function."""
        rv = self.preprocess_request()
        if rv is None:
            rv = self.dispatch_request()
        response = self.make_response(rv)
        response = self.process_response(response)
        request_finished.send(self, response=response)
        return response
    
    def preprocess_request(self):
        """Preprocess the request."""
        return None
    
    def dispatch_request(self):
        """Dispatch the request to the appropriate view function."""
        return self.view_functions.get('index', lambda: 'Hello World')()
    
    def make_response(self, rv):
        """Create a response object."""
        from .wrappers import Response
        if isinstance(rv, Response):
            return rv
        return Response(rv)
    
    def process_response(self, response):
        """Process the response."""
        return response
    
    def handle_exception(self, e):
        """Handle an exception."""
        from .wrappers import Response
        return Response(f'Error: {str(e)}', status=500)
    
    def __call__(self, environ, start_response):
        """Make the app callable."""
        return self.wsgi_app(environ, start_response)