import os
import re
import sys
import time
import logging
import logging.handlers

from math import pi
from datetime import datetime

from bokeh.charts import cursession
from bokeh.plotting import figure, output_server, show
from bokeh.models import DatetimeTickFormatter, GlyphRenderer
from bokeh.io import vplot
from bokeh.models.ranges import Range1d

log = logging.getLogger(__name__)

# hack to hide messages if we log before setting up handler
logging.root.manager.emittedNoHandlerWarning = True

def setup_logging(filename=None, log_level=logging.DEBUG, max_size=100000, rollovers=3):
    """Easy to use logging - on reload it will not add multiple stdout handlers
    @param filename: full path to log file or None to indicate stdout
    """
    root_logger = logging.getLogger("")
    root_logger.setLevel(log_level)

    if filename:
      handler = logging.handlers.RotatingFileHandler(filename, 'a', max_size, rollovers)
    else:
      handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter("%(asctime)s:%(levelname)9s:%(name)20s: %(message)s")
    handler.setFormatter(formatter)

    add_handler = True
    for handle in root_logger.handlers:
        try:
            if handle.baseFilename == handler.baseFilename:
                add_handler = False
                duplicate_handler = handler.baseFilename
                break
        except AttributeError, e:
            # handlers without baseFilename
            root_logger.debug(str(e))
            pass

    if add_handler:
        root_logger.debug("Added handler to the root logger.")
        root_logger.addHandler(handler)
    else:
        root_logger.debug("Duplicate logging handler: %s" % (duplicate_handler,))


def tail_generator(filename=os.path.expanduser("./temp.log"), interval=0.5,
                   exit_after=0):
    """
    Reads file and then `tails` it -- checking at interval seconds
    Adapted from: http://code.activestate.com/recipes/157035-tail-f-in-python/
    """
    with open(filename, 'r') as f:
        failed = 0
        while True:
            where = f.tell()
            line = f.readline()
            if not line:
                failed += 1
                if exit_after != 0 and failed > exit_after:
                    return
                time.sleep(interval)
                f.seek(where)
            else:
                failed = 0
                yield line

def parse_line(line):
    """convert a line of data from this to objects '<temp>|<datetime>' """
    result = [None, None]
    line = line.strip()
    try:
        temp, date = line.split("|")
    except ValueError:
        log.info("Bad line: can't split: %s" % (line,))
        return result

    z = time.mktime(time.strptime(date, "%d-%m-%y-%H:%M:%S"))
    dt_object = datetime.fromtimestamp(z)

    # remove F:  "80.0 F"
    try:
        temp = float(temp.split()[0])
    except IndexError:
        log.info("Bad temp: %s" % (temp,))
        return result

    result = [temp, dt_object]
    log.debug("Returning %s" % (result,))
    return result

def decimate(gen, skip=10):
    """If the generated is depleted, return a blank string"""
    for skip in xrange(skip):
        try:
            line = gen.next()
        except StopIteration:
            return ""
    return line

def update_series(ds, xvalue, yvalue):
    ds.data['x'].append(xvalue)
    ds.data['y'].append(yvalue)
    cursession().store_objects(ds)

def main():
    setup_logging()
    logging.getLogger("requests").setLevel(logging.WARNING)

    output_server("Temp Chart")

    window = 100
    width = 800
    height = 200

    # line chart
    line_fig = figure(plot_width=width, plot_height=height)
    line = line_fig.line(x=[], y=[])

    # circle chart
    c_fig = figure(plot_width=width, plot_height=height)
    circle = c_fig.circle(x=[], y=[], size=1)

    # format axes
    line_fig.xaxis[0].formatter = DatetimeTickFormatter(formats=dict(days=["%F %T"]))
    line_fig.xaxis.major_label_orientation = pi/4
    c_fig.xaxis[0].formatter = DatetimeTickFormatter(formats=dict(days=["%F %T"]))
    c_fig.xaxis.major_label_orientation = pi/4

    p = vplot(line_fig, c_fig)
    show(p)

    line_ds = line.select(dict(type=GlyphRenderer))[0].data_source
    circle_ds = circle.select(dict(type=GlyphRenderer))[0].data_source

    lines = tail_generator(exit_after=2)
    if True:
        for line in lines:
            line = decimate(lines, skip=300)
            temp, date = parse_line(line)
            if temp is None:
                continue
            update_series(line_ds, date, temp)
            update_series(circle_ds, date, temp)
            time.sleep(0.01)

    return c_fig, circle

if __name__ == "__main__":
    main()
