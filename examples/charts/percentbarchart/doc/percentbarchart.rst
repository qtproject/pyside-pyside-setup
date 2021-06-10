Percent Bar Chart Example
=========================

The example shows how to create a simple percent bar chart.

A percent bar chart shows the data in sets as a percentage of all sets per
category.

Creating percent bar charts is just like creating a regular bar chart, except
that for a percent bar charts, we use the QPercentBarSeries API instead of
QBarSeries. Also, in the bar chart, we used the nice numbers algorithm to make
the y-axis numbering look better. With the percent bar chart there is no need
for that, because the maximum y-axis value is always 100.

.. image:: percentbarchart.png
   :width: 400
   :alt: Percent Bar Chart Screenshot
