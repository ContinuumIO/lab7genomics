from os.path import join

import numpy as np

from bokeh.server.server_backends import (
    AbstractDataBackend
)
from . import sam_backend
cache = {}

class GenomicDataBackend(AbstractDataBackend):
    def __init__(self, directory):
        self.directory = directory

    def genomic_coverage_downsample(self, request_username, data_url, data_parameters):
        """
        Read in the SAM and setup the index/meta data structures
        """
        fname = join(self.directory, data_url)
        if fname in cache:
            backend = cache[fname]
        else:
            backend = sam_backend.SAMBackend(fname)
            cache[fname] = backend
        [primary_column, domain_name, domain_limit, domain_resolution] = data_parameters
        counts = backend.data_column(primary_column, domain_name, domain_limit, domain_resolution)
        coords = np.linspace(domain_limit[0], domain_limit[1], domain_resolution)
        return {'data' : {'counts' : counts, domain_name : coords}}

    def get_data(self, request_username, datasource, parameters, plot_state):
        data_url = datasource.data_url
        resample_op = datasource.transform['resample']
        if resample_op == 'genomic_coverage':
            return self.genomic_coverage_downsample(
                request_username, data_url,
                parameters)
        else:
          raise ValueError("Unknown resample op '{}'".format(resample_op))
