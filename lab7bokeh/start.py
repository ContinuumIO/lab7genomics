import uuid
from collections import OrderedDict

import pandas as pd
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
from bokeh.objects import ServerDataSource, Range1d, HoverTool, ColumnDataSource, GridPlot
from bokeh.widgetobjects import VBox
from bokeh.server.utils.plugins import object_page
from bokeh.server.utils.reload import robust_reloader
from bokeh.plotting import line, hold, figure, quad, rect, curplot
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

def make_plot(xr):
    yr = Range1d(start=-10, end=10)
    figure(plot_width=800, plot_height=350,
           y_range=yr,
           x_range=xr,
           tools="xpan,xwheel_zoom,hover,box_zoom,reset")
    hold()
    genes = pd.read_csv('/home/hugoshi/data/lab7/genes.refseq.hg19.bed', sep='\t',
                        skiprows=[0], header=None)
    genes.rename(columns={
        0: "chromosome",
        1: "start",
        2: "end"},
                 inplace=True
    )
    genes = genes[genes.chromosome == 'chr5']
    g_len = len(genes)
    quad(genes.start - 0.5,      # left edge
         genes.end - 0.5,        # right edge
         [2.3] * g_len,            # top edge
         [1.7] * g_len,
         ['blue'] * g_len)           # bottom edge
    exons = pd.read_csv('/home/hugoshi/data/lab7/exons.refseq.hg19.bed', sep='\t', skiprows=[0], header=None)
    exons.columns = ["chromosome", "start", "end", "meta1", "meta2", "meta3"]
    exons = exons[exons.chromosome == 'chr5']
    e_len = len(exons)
    quad(exons.start - 0.5,      # left edge
         exons.end - 0.5,        # right edge
         [1.3] * e_len,            # top edge
         [0.7] * e_len,
         ['blue'] * e_len)           # bottom edge

    df = pd.read_csv('/home/hugoshi/data/lab7/CHP2.20131001.hotspots.bed', sep='\t', skiprows=[0], header=None)
    df.columns = ["chromosome", "start", "end", "meta1", "meta2", "meta3"]
    df = df[df.chromosome == 'chr5']
    singles = df[df.start+1 == df.end]
    widers = df[df.start+1 != df.end]
    slen = len(singles)
    wlen = len(widers)
    s_source = ColumnDataSource(
    data = dict(
        start=singles.start,
        end=singles.end,
        meta1=singles.meta1,
        meta2=singles.meta2,
        meta3=singles.meta3))
    rect('start',    # x center
         [1]*slen,         # y center
         [0.9]*slen,
         [1]*slen,
         color=['red']*slen,
         source=s_source)         # height
    hover = [t for t in curplot().tools if isinstance(t, HoverTool)][0]
    hover.tooltips = OrderedDict([
        # add to this
        ("position", "@start"),
        ("meta 1", "@meta1"),
        ("meta 2", "@meta2"),
        ("meta 3", "@meta3")
    ])

    quad(widers.start - 0.5,      # left edge
         widers.end - 0.5,        # right edge
         [0.3] * wlen,            # top edge
         [-0.3] * wlen)           # bottom edge

    hold()
    return curplot()

@bokeh_app.route("/plot")
@object_page("plot")
def annotations():
    return make_plot()

@bokeh_app.route("/histogram")
@object_page("histogram")
def make_object():
    source = ServerDataSource(data_url="IonXpress_004_rawlib.sam",
                              owner_username="defaultuser",
                              transform={'resample' : 'genomic_coverage',
                                         'primary_column' : 'coverage',
                                         'domain_name' : 'chr5'},
                              data={})
    x_range = Range1d(start=0, end=249250621)
    plot1 = line('chr5', 'counts', tools="pan,wheel_zoom,box_zoom,reset,previewsave",
                plot_width=800, plot_height=350,
                source=source, x_range=x_range)
    plot2 = make_plot(x_range)
    return VBox(children=[plot1, plot2])
    #return VBox(children=[plot1])

if __name__ == "__main__":
    import logging
    logging.basicConfig(leve=logging.DEBUG)
    start_server()
