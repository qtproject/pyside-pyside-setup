.. _translations:

Translating Applications
========================

GNU gettext
-----------

The `GNU gettext <https://docs.python.org/3/library/gettext.html>`_ module
can be used to provide translations for applications.

The ``examples/widgets/gettext`` example illustrates this. The example is
very simple, it has a menu and shows a list of programming languages with
multiselection.

Translation works by passing the message strings through function calls that
look up the translation. It is common to alias the main translation function
to ``_``. There is a special translation function for sentences that contain
a plural form depending on a count ("{0} items(s) selected"). It is commonly
aliased to ``ngettext``.

Those functions are defined at the top:

    .. code-block:: python

        import gettext
        ...
        _ = None
        ngettext = None

and later assigned as follows:

    .. code-block:: python

        src_dir = Path(__file__).resolve().parent
        try:
            translation = gettext.translation('example', localedir=src_dir / 'locales')
            if translation:
                translation.install()
                _ = translation.gettext
                ngettext = translation.ngettext
        except FileNotFoundError:
            pass
        if not _:
            _ = gettext.gettext
            ngettext = gettext.ngettext

This specifies that our translation file has the base name ``example`` and
will be found in the source tree under ``locales``. The code will try
to load a translation matching the current language.

Messages to be translated look like:

    .. code-block:: python

        file_menu = self.menuBar().addMenu(_("&File"))

The status bar message shown in response to a selection change uses
a plural form depending on a count:

    .. code-block:: python

        count = len(self._list_widget.selectionModel().selectedRows())
        message = ngettext("{0} language selected",
                           "{0} languages selected", count).format(count)

The ``ngettext()`` function takes the singular form, plural form and the count.
The returned string still contains the formatting placeholder, so it needs
to be passed through ``format()``.

In order to translate the messages to say German, a template file (``.pot``)
is first created:

.. code-block:: bash

    mkdir -p locales/de_DE/LC_MESSAGES
    xgettext -L Python -o locales/example.pot main.py

This file has a few generic placeholders which can be replaced by the
appropriate values.  It is then copied to the ``de_DE/LC_MESSAGES`` directory.

    .. code-block:: bash

        cd locales/de_DE/LC_MESSAGES/
        cp ../../example.pot .

Further adaptions need to be made to account for the German plural
form and encoding:

    .. code-block::

        "Project-Id-Version: PySide6 gettext example\n"
        "POT-Creation-Date: 2021-07-05 14:16+0200\n"
        "Language: de_DE\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=UTF-8\n"
        "Content-Transfer-Encoding: 8bit\n"
        "Plural-Forms: nplurals=2; plural=n != 1;\n"

Below, the translated messages can be given:

    .. code-block::

        #: main.py:57
        msgid "&File"
        msgstr "&Datei"

Finally, the ``.pot`` is converted to its binary form (machine object file,
``.mo``), which needs to be deployed:

    .. code-block:: bash

        msgfmt -o example.mo example.pot

The example can then be run in German:

    .. code-block:: bash

        LANG=de python main.py
