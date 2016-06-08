import discover
import json

def app(environ, start_response):
  data = discover.post_playlist(environ)
  status = '200 OK'
  response_headers = [('Content-Type', 'text/plain'),
                  ('Content-Length', str(len(data)))]
  start_response(status,response_headers)
  return [data]
