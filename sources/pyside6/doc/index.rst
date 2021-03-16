|project|
*********

.. ifconfig:: output_format == 'html'

    **Qt for Python** offers the official Python bindings for `Qt`_, and
    has two main components:

    * `PySide6`_, so that you can use Qt6 APIs in your Python applications, and
    * `Shiboken6 <shiboken6/index.html>`__, a binding generator tool, which can
      be used to expose C++ projects to Python, and a Python module with
      some utility functions.

.. ifconfig:: output_format == 'qthelp'

    **Qt for Python** offers the official Python bindings for `Qt`_, and
    has two main components:

    * `PySide6`_, so that you can use Qt6 APIs in your Python applications, and
    * `Shiboken6 <../shiboken6/index.html>`__, a binding generator tool, which can
      be used to expose C++ projects to Python, and a Python module with
      some utility functions.

`Porting from PySide2 to PySide6`_ provides information on porting existing PySide2
applications.

This project is available under the LGPLv3/GPLv3 and the `Qt commercial license`_.

.. _Qt: https://doc.qt.io
.. _PySide6: quickstart.html
.. _`Qt commercial license`: https://www.qt.io/licensing/
.. _`Porting from PySide2 to PySide6`: porting_from2.html



Documentation
=============

.. ifconfig:: output_format == 'html'

    .. panels::
        :body: text-center
        :container: container-lg pb-3
        :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2

        Write your first Qt application.

        +++

        .. link-button:: quickstart
            :type: ref
            :text: Check it out!
            :classes: btn-qt btn-block stretched-link
        ---

        Install and build from source.

        +++

        .. link-button:: gettingstarted
            :type: ref
            :text: Getting Started
            :classes: btn-qt btn-block stretched-link
        ---

        PySide API reference.

        +++

        .. link-button:: api
            :type: ref
            :text: API Docs
            :classes: btn-qt btn-block stretched-link

        ---

        Learn with step-by-step guides.

        +++

        .. link-button:: tutorials/index
            :type: ref
            :text: Tutorials
            :classes: btn-qt btn-block stretched-link
        ---

        Check all the available examples.

        +++

        .. link-button:: examples/index
            :type: ref
            :text: Examples
            :classes: btn-qt btn-block stretched-link
        ---

        Watch webinars, talks, and more.

        +++

        .. link-button:: videos
            :type: ref
            :text: Videos
            :classes: btn-qt btn-block stretched-link

        ---

        Learn to deploy your applications.

        +++

        .. link-button:: deployment-guides
            :type: ref
            :text: Deployment
            :classes: btn-qt btn-block stretched-link
        ---

        API differences and known issues.

        +++

        .. link-button:: considerations
            :type: ref
            :text: Considerations
            :classes: btn-qt btn-block stretched-link
        ---

        Generate C++ to Python bindings.

        +++

        .. link-button:: shiboken6/index.html
            :text: Shiboken
            :classes: btn-qt btn-block stretched-link

.. ifconfig:: output_format == 'qthelp'

    .. raw:: html

        <table class="special">
            <colgroup>
                <col style="width: 33%" />
                <col style="width: 33%" />
                <col style="width: 33%" />
            </colgroup>
            <tr>
                <td><a href="quickstart.html"><p><strong>Check It Out!</strong><br/>Write your first Qt app.</p></a></td>
                <td><a href="gettingstarted.html"><p><strong>Getting Started</strong><br/>Install and build from source.</p></a></td>
                <td><a href="api.html"><p><strong>API Docs</strong><br/>Qt for Python API reference.</p></a></td>
            </tr>
            <tr>
                <td><a href="tutorials/index.html"><p><strong>Tutorials</strong><br/>Learn with step-by-step guides.</p></a></td>
                <td><a href="examples/index.html"><p><strong>Examples</strong><br/>Check all the available examples.</p></a></td>
                <td><a href="videos.html"><p><strong>Videos</strong><br/>Watch webinars, Talks, and more.</p></a></td>
            </tr>
            <tr>
                <td><a href="deployment.html" style="display: block;"><p><strong>Deployment</strong><br/>Learn to deploy your apps.</p></a></td>
                <td><a href="considerations.html" style="display: block;"><p><strong>Considerations</strong><br/>API differences and known issues.</p></a></td>
                <td><a href="../shiboken6/index.html" style="display: block;"><p><strong>Shiboken</strong><br/>Generate C++ to Python binding.</p></a></td>
            </tr>
        </table>


We have also a `wiki page`_ where you can find how to report bugs, contribute or contact the community.

.. _`wiki page`: https://wiki.qt.io/Qt_for_Python

.. toctree::
   :hidden:
   :glob:

   contents.rst
   gettingstarted*
   overviews/*
