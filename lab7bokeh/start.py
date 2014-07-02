import uuid

import werkzeug

from bokeh.settings import settings
import bokeh.server as bokehserver
from bokeh.server.server_backends import (
    RedisServerModelStorage,
    SingleUserAuthentication
)
from bokeh.server.serverbb import RedisBackboneStorage
from bokeh.server.app import bokeh_app
from bokeh.server import services
from bokeh.server.start import register_blueprint, start_app

def start_server():
    backend = {
        "redis_port": 7020,
        "start_redis": True,
    }
    rhost = backend.get('redis_host', '127.0.0.1')
    rport = backend.get('redis_port', REDIS_PORT)
    bbstorage = RedisBackboneStorage(redis.Redis(host=rhost, port=rport, db=2))
    servermodel_storage = RedisServerModelStorage(redis.Redis(host=rhost, port=rport, db=3))
    authentication = SingleUserAuthentication()
    bokeh_app.setup(backend, bbstorage, servermodel_storage,
                    authentication, None)
    if not app.secret_key:
        app.secret_key = str(uuid.uuid4())
    def helper():
        start_server(args)
    helper = robust_reloader(helper)
    extra_files = settings.js_files() + settings.css_files()
    werkzeug.serving.run_with_reloader(
        helper, extra_files=extra_files)
    start_app(host="0.0.0.0", port=5010, verbose=True)

@bokeh_app.route("/myapp")
@object_page("myapp")
def make_object():
    autompg['cyl'] = autompg['cyl'].astype(str)
    autompg['origin'] = autompg['cyl'].astype(str)
    app = CrossFilter.create(df=autompg)
    return app
