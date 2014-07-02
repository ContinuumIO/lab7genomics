import uuid

import redis
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
from bokeh.server.start import register_blueprint, start_app, app
from bokeh.objects import ServerDataSource, Range1d
from bokeh.server.utils.plugins import object_page
from bokeh.server.utils.reload import robust_reloader
from bokeh.plotting import line
import bokeh.settings as settings

from lab7bokeh.data_backend import GenomicDataBackend

def start_server():
    from bokeh.server.views import deps
    app.debug = True
    bokeh_app.debug = True
    bokeh_app.splitjs = True
    bokeh_app.debugjs = True
    settings.debugjs = True
    backend = {
        "type" : "redis",
        "redis_port": 7020,
        "start_redis": True,
    }
    rhost = backend.get('redis_host')
    rport = backend.get('redis_port')
    bbstorage = RedisBackboneStorage(redis.Redis(host=rhost, port=rport, db=2))
    servermodel_storage = RedisServerModelStorage(redis.Redis(host=rhost, port=rport, db=3))
    authentication = SingleUserAuthentication()
    data_backend = GenomicDataBackend("/home/hugoshi/data/lab7/")
    bokeh_app.setup(backend, bbstorage, servermodel_storage,
                    authentication, data_backend)
    register_blueprint()
    start_app(host="0.0.0.0", port=5010, verbose=True)

@bokeh_app.route("/histogram")
@object_page("histogram")
def make_object():
    source = ServerDataSource(data_url="IonXpress_004_rawlib.sam",
                              owner_username="defaultuser",
                              transform={'resample' : 'genomic_coverage',
                                         'primary_column' : 'coverage',
                                         'domain_name' : 'chr1'},
                              data={})
    x_range = Range1d(start=0, end=249250621)
    plot = line('chr1', 'counts', tools="pan,wheel_zoom,box_zoom,reset,previewsave",
                source=source, x_range=x_range)
    return plot

if __name__ == "__main__":
    import logging
    logging.basicConfig(leve=logging.DEBUG)
    start_server()
