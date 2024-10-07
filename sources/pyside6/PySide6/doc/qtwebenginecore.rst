// @snippet qwebenginepage-async-note
.. note:: We guarantee that the ``resultCallback`` is always called, but it
          might be done during page destruction. When ``QWebEnginePage``
          is deleted, the callback is triggered with an invalid value and it
          is not safe to use the corresponding ``QWebEnginePage``,
          ``QWebEngineFrame``, or ``QWebEngineView`` instance inside it.
// @snippet qwebenginepage-async-note

// @snippet qwebenginepage-findtext
Finds the specified string, ``subString``, in the page, using the given
``options``. The ``findTextFinished()`` signal is emitted when a string search
is completed.

To clear the search highlight, just pass an empty string.

The ``resultCallback`` must take a ``QWebEngineFindTextResult`` parameter.
// @snippet qwebenginepage-findtext

// @snippet qwebenginepage-tohtml
Asynchronous method to retrieve the page's content as HTML, enclosed in HTML
and BODY tags. Upon successful completion, ``resultCallback`` is called with
the page's content.
// @snippet qwebenginepage-tohtml

// @snippet qwebenginepage-toplaintext
Asynchronous method to retrieve the page's content converted to plain text,
completely stripped of all HTML formatting.

Upon successful completion, ``resultCallback`` is called with the page's content.
// @snippet qwebenginepage-toplaintext

// @snippet qwebenginepage-runjavascript
Runs the JavaScript code contained in ``scriptSource`` script on this frame,
without checking whether the DOM of the page has been constructed.

To avoid conflicts with other scripts executed on the page, the world in which
the script is run is specified by ``worldId``. The world ID values are the same
as provided by ``QWebEngineScript.ScriptWorldId``, and between 0 and 256. If
you leave out the world ID, the script is run in the ``MainWorld`` (0).

When the script has been executed, the callable ``resultCallback`` is called
with the result of the last executed statement.

Only plain data can be returned from JavaScript as the result value.

.. note:: Do not execute lengthy routines in the callback function, because
          it might block the rendering of the web engine page.
// @snippet qwebenginepage-runjavascript
