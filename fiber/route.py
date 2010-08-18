import re

class Route(object):
    def __init__(self, pattern, environ):
        self.method, path_pattern = self.split_pattern(pattern)
        self.path_regex = self.path_pattern_to_regex(path_pattern)
        self.request_method = environ['REQUEST_METHOD']
        self.request_path = environ['PATH_INFO']
    
    def match(self):
        return True if self.match_method() and self.match_path() else False
    
    def match_method(self):
        return self.method is None or self.method == self.request_method
        #return self.method == self.request_method if self.method is not None else True
    
    def match_path(self):
        return re.match(self.path_regex, self.request_path, re.I)
    
    def path_params(self):
        return self.match_path().groupdict()
    
    @classmethod
    def split_pattern(cls, pattern):
        elements = str.split(pattern, ' ')
        #raise ValueError(len(elements))
        if len(elements) == 2:
            method, path_pattern = elements
        elif len(elements) == 1:
            method, path_pattern = None, elements.pop()
        else:
            raise ValueError("Bad format of route template: " + pattern)
        return method, path_pattern
    
    @classmethod
    def path_pattern_to_regex(cls, path_pattern):
        """Przerabia /ple/ple/{id} na regex"""
        pattern = path_pattern
        var_regex = re.compile(r'\{(\w+)(?::([^}]+))?\}', re.VERBOSE)
        regex = ''
        last_pos = 0
        for match in var_regex.finditer(pattern):
          regex += re.escape(pattern[last_pos:match.start()])
          var_name = match.group(1)
          expr = match.group(2) or '[^/]+'
          expr = '(?P<%s>%s)' % (var_name, expr)
          regex += expr
          last_pos = match.end()
        regex += re.escape(pattern[last_pos:])
        regex = '^%s$' % regex
        return regex