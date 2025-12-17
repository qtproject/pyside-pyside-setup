.. _tutorial_add_chart:


Chapter 5 - Add a chart view
=============================

A table is nice to present data, but a chart is even better. For this, you
need the QtGraphs module that provides many types of plots and options to
graphically represent data.

The relevant class for a plot is the GraphsView QML type, to which axes and
data series can be added. As a first step, try including then without any data
to plot.

Make the following highlighted changes to :code:`main_widget.py` from the
previous chapter to add a chart:

.. literalinclude:: datavisualize5/main_widget.py
   :linenos:
   :lines: 5-
   :emphasize-lines: 4,27-39,53
