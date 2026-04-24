"""Visualization functions for GNSS data.

"""

__authors__ = "D. Knowles"
__date__ = "27 Jan 2022"

import numpy as np
import matplotlib.pyplot as plt

from gnss_lib_py.visualizations.style import *
from gnss_lib_py.navdata.navdata import NavData

def plot_metric(navdata, *args, groupby=None, avg_y=False, fig=None,
                title=None, save=False, prefix="", fname=None,
                markeredgecolor="k", markeredgewidth=0.2, **kwargs):
    """Plot specific metric from a row of the NavData class.

    Parameters
    ----------
    navdata : gnss_lib_py.navdata.navdata.NavData
        Instance of the NavData class
    *args : tuple
        Tuple of row names that are to be plotted. If one is given, that
        value is plotted on the y-axis. If two values are given, the
        first is plotted on the x-axis and the second on the y-axis.
    groupby : string
        Row name by which to group and label plots.
    avg_y : bool
        Whether or not to average across the y values for each x
        timestep when doing groupby
    fig : matplotlib.pyplot.Figure
         Previous figure on which to add current plotting. Default of
         None plots on a new figure.
    title : string
        Title for the plot.
    save : bool
        Saves figure if true to file specified by fname or defaults
        to the Results folder otherwise.
    prefix : string
        File prefix to add to filename.
    fname : string or path-like
        Path to save figure. If not None, fname is passed directly
        to matplotlib's savefig fname parameter and prefix will be
        overwritten.
    markeredgecolor : color
        Marker edge color.
    markeredgewidth : float
        Marker edge width.

    Returns
    -------
    fig : matplotlib.pyplot.Figure
         Figure of plotted metrics.

    """
    pass

def plot_metric_by_constellation(navdata, *args, save=False, prefix="",
                                 fname=None, **kwargs):
    """Plot specific metric from a row of the NavData class.

    Breaks up metrics by constellation names in "gnss_id" and
    additionally "signal_type" if the "signal_type" row exists.

    Plots will include a legend with satellite ID if the "sv_id" row
    is present in navdata.

    Parameters
    ----------
    navdata : gnss_lib_py.navdata.navdata.NavData
        Instance of the NavData class. Must include ``gnss_id`` row and
        optionally ``signal_type`` and ``sv_id`` for increased
        labelling.
    *args : tuple
        Tuple of row names that are to be plotted. If one is given, that
        value is plotted on the y-axis. If two values are given, the
        first is plotted on the x-axis and the second on the y-axis.
    save : bool
        Saves figure if true to file specified by ``fname`` or defaults
        to the Results folder otherwise.
    prefix : string
        File prefix to add to filename.
    fname : string or path-like
        Path to save figure to. If not None, ``fname`` is passed
        directly to matplotlib's savefig fname parameter and prefix will
        be overwritten.

    Returns
    -------
    fig : list of matplotlib.pyplot.Figure objects
         List of figures of plotted metrics.

    """
    pass

def _parse_metric_args(navdata, *args):
    """Parses arguments and raises error if metrics are nonnumeric.

    Parameters
    ----------
    navdata : gnss_lib_py.navdata.navdata.NavData
        Instance of the NavData class
    *args : tuple
        Tuple of row names that are to be plotted. If one is given, that
        value is plotted on the y-axis. If two values are given, the
        first is plotted on the x-axis and the second on the y-axis.

    Returns
    -------
    x_metric : string
        Metric to be plotted on y-axis if y_metric is None, otherwise
        x_metric is plotted on x axis.
    y_metric : string or None
        y_metric is plotted on the y axis.

    """
    pass

def _get_new_fig(fig=None):
    """Creates new default figure and axes.

    Parameters
    ----------
    fig : matplotlib.pyplot.figure
        Previous figure to format to style.

    Returns
    -------
    fig : matplotlib.pyplot.figure
        Default NavData figure.
    axes : matplotlib.pyplot.axes
        Default NavData axes.

    """
    pass
