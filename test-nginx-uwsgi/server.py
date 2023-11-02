# def application(env, start_response):
#     start_response('200 OK', [('Content-Type','text/html')])
#     return [b"Hello World\n"]
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html'), ('X-Cache', 'HIT' if env.get('HTTP_X_UWSGI_CACHE_STATUS') == 'HIT' else 'MISS')])
    return [b"Hello World\n"]
