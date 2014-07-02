# Bokeh backend for same files
import numpy as np

class SAMBackend(object):

  def __init__(self, url):
    """
    Read in the SAM and setup the index/meta data structures
    """

    lines = [l.strip().split() for l in open(url)]

    # Split the lines and the headers
    i = 0
    self.refs = {} # name: [len, offset-to-first-record, offset-to-last-record + 1]

    while(lines[i][0][0] == '@'):
      line = lines[i]
      if line[0] == '@SQ':
        sn = line[1].split(':')[1]
        ln = int(line[2].split(':')[1])
        self.refs[sn] = [ln, None, None]
      i += 1

    # Process the mapped reads
    # - create offset pointers to the start of each chromosome
    # - convert the position to an int
    cur_chr = lines[i][2]
    self.refs[cur_chr][1] = i
    
    while(i < len(lines)):
      if not (int(lines[i][1]) & 0x4): 
        lines[i][3] = int(lines[i][3])

        if lines[i][2] != cur_chr:
          self.refs[cur_chr][2] = i # mark the end
          cur_chr = lines[i][2]     
          self.refs[cur_chr][1] = i # mark the start
      i += 1

    self.lines = lines
    
    return


  def _coverage(self, chr, limit, nbins):
    """
    Compute the coverage counts for a region of a chromosome

    -- is resolution the bin size??
    """

    c = np.zeros(nbins, dtype=np.int)
    chr_start, chr_stop = self.refs[chr][1:]
    bin_size = float((limit[1] - limit[0]) / nbins)

    for i in range(chr_start, chr_stop):
      read_start = self.lines[i][3]
      read_len   = len(self.lines[i][9])

      start_bin = int((read_start - limit[0]) / bin_size)
      stop_bin = int((read_start + read_len - limit[0]) / bin_size)

      # print start_bin, stop_bin
      c[start_bin:stop_bin + 1] += 1
    
    return c

  def data_column(self, primary_column, domain_name, domain_limit, domain_resolution):
    ret_val = None
    if primary_column == 'coverage':
      ret_val = self._coverage(domain_name, domain_limit, domain_resolution)
      
    return ret_val

if __name__=='__main__':
  import sys

  sb = SAMBackend(sys.argv[1])
  c = sb.data_column('coverage', 'chr1', [0, 249250621], 1)
  print c, sum(c)
  
  c = sb.data_column('coverage', 'chr1', [0, 249250621], 10)  
  print c, sum(c)

  c = sb.data_column('coverage', 'chr1', [0, 249250621], 100)  
  print c, sum(c)

