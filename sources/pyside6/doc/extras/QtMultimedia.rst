    .. image:: images/noun_Media_166644.svg

The Qt Multimedia module provides APIs for playing back and recording
audiovisual content

Qt Multimedia is an add-on module that provides a rich set of QML types and C++
classes to handle multimedia content. It contains an easy to use API for
playing back audio and video files and rendering those on screen, as well as a
comprehensive API for recording audio and video from various sources, including
system cameras and microphones, screen or window captures, and audio or video
memory buffers.

The functionality of this module is divided into the following submodules:

    +-----------------------------------+----------------------------------------------------------+
    |:ref:`Multimedia-Overview`         |Provides an API for multimedia-specific use cases.        |
    +-----------------------------------+----------------------------------------------------------+
    |:mod:`PySide6.QtMultimediaWidgets` |Provides a widget-based multimedia API.                   |
    +-----------------------------------+----------------------------------------------------------+
    |:mod:`PySide6.QtSpatialAudio`      |Provides an API for implementing sound fields in 3D space.|
    +-----------------------------------+----------------------------------------------------------+

Getting started
^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtMultimedia


Overviews and important topics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * :ref:`Multimedia-Overview`
    * :ref:`Audio-Overview`
    * :ref:`Spatial-Audio-Overview`
    * :ref:`Video-Overview`
    * :ref:`Camera-Overview`
    * :ref:`overviews_supported-media-formats`

Target platform and backend notes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Qt Multimedia offers user-friendly, cross-platform APIs for media playback,
recording, and device management. The implementation of core APIs, including
:class:`~PySide6.QtMultimedia.QMediaDevices` ,
:class:`~PySide6.QtMultimedia.QAudioDevice` ,
:class:`~PySide6.QtMultimedia.QSoundEffect` ,
:class:`~PySide6.QtMultimedia.QAudioSink` , and
:class:`~PySide6.QtMultimedia.QAudioSource` are integrated into
the main Qt Multimedia library, eliminating the need for additional libraries.
Other Qt Multimedia APIs are implemented using plugin libraries known as media
backends. The main media backend, built on `FFmpeg`_ ,
ensures seamless cross-platform functionality, and is the default on all
platforms except WebAssembly and embedded Linux/Boot2Qt. With Boot2Qt, the
default backend is built on top of `GStreamer`_, but the FFmpeg media backend
can be enabled using the ``QT_MEDIA_BACKEND`` environment variable.

The FFmpeg backend
==================

The FFmpeg media backend relies on the **FFmpeg 7.1.3** libraries, which are
included with the Qt Online Installer and tested by the maintainers. The binary
packages from the online installer use dynamic linking to FFmpeg. Therefore,
applications must either bundle FFmpeg binaries in their installer or depend on
FFmpeg being installed on the operating system. The FFmpeg libraries are
automatically deployed using Qt's deployment tools as described in the
Deploying Qt Applications documentation, except for Linux/X11. Applications can
also deploy their own build of FFmpeg, either as shared or static libraries,
provided the FFmpeg major version matches the version used by Qt.

While Qt Multimedia leverages the FFmpeg media backend on most operating
systems, platform specific functional or visual differences may arise between
applications on different platforms. FFmpeg does not provide identical codec
and format support across all platforms, and the performance of Qt Multimedia
features may depend on hardware support that is only available on certain
platforms. For instance, FFmpeg encounters specific issues with hardware
acceleration on Linux targets with ARM architectures. Therefore, it is
recommended to test Qt Multimedia applications on all target platforms.

.. note:: The FFmpeg project provides features under various licenses. The pre-built
          FFmpeg libraries that are provided through the Online Installer are only
          including features that agree with the permissive licenses listed under
          `Licenses and attributions`_.

To ease development and debugging, some FFmpeg functionality is configurable
via :ref:`Advanced-FFmpeg-Configuration` which are part
of the private Qt Multimedia API.

Native backends
===============

For compatibility with existing applications, we maintain native media backends
for each operating system:

    * :ref:`Qt-Multimedia-GStreamer-backend` on Embedded Linux
    * AVFoundation on macOS and iOS
    * WebAudio and WebVideo on WebAssembly

.. note:: The FFmpeg media backend is the default backend except on
          WebAssembly, native backends are still available but with **limited**
          support. The GStreamer backend is only available on Linux, and is
          only recommended for embedded applications.

Qt Maintainers will strive to fix critical issues with the native backends but
don't guarantee fixing minor issues, including inconsistent behavior across
platforms. New features will only be implemented on the FFmpeg media backend,
with the exception of WebAssembly.

The GStreamer backend has some private APIs to allow more fine-grained control.
However, there are known bugs in the GStreamer backend. More details can be
found in :ref:`Qt-Multimedia-GStreamer-backend`.

Backend limitations will be documented, and their status will be maintained in
the respective classes.

Changing backends
=================

In the case of issues with the default FFmpeg backend, we suggest testing with
a native backend. You can switch to native backends by setting the
``QT_MEDIA_BACKEND`` environment variable to ``windows``\, ``gstreamer`` (on
Embedded Linux), ``darwin`` (on macOS and iOS), or ``android``\:

    ::

            export QT_MEDIA_BACKEND=darwin


To force assign FFmpeg as the used backend, set the variable to ``ffmpeg``\:

    ::

            export QT_MEDIA_BACKEND=ffmpeg


On the Qt Multimedia compilation stage, the default media backend can be
configured via cmake variable ``QT_DEFAULT_MEDIA_BACKEND``\.

Target platform notes
=====================

The following pages list issues for specific target platforms.

    * :ref:`Qt-Multimedia-on-macOS-and-iOS`
    * :ref:`Qt-Multimedia-on-WebAssembly`
    * :ref:`Qt-Multimedia-on-Windows`
    * :ref:`Qt-Multimedia-on-Linux`
    * :ref:`Qt-Multimedia-GStreamer-backend`

Permissions
^^^^^^^^^^^

Starting from Qt 6.6, the Qt Multimedia module uses new
:class:`~PySide6.QtCore.QPermission` API to handle
:class:`~PySide6.QtCore.QCameraPermission` and
:class:`~PySide6.QtCore.QMicrophonePermission` permissions.

This means that Qt itself no longer queries for these permissions, so this
needs to be done directly from the client application.

Please refer to the :ref:`Application-Permissions` page for an example of how to
integrate the new QPermission API into the application.

.. _`FFmpeg`: http://ffmpeg.org/
.. _`GStreamer`: https://gstreamer.freedesktop.org/
.. _`Licenses and attributions`: https://doc.qt.io/qt-6/qtmultimedia-index.html#licenses-and-attributions
