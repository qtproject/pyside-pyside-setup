    .. image:: images/noun_Media_166644.svg

The Qt Multimedia module provides APIs for playing back and recording audiovisual content

Qt Multimedia is an add-on module that provides a rich set of QML types and C++
classes to handle multimedia content. It contains an easy to use API for
playing back audio and video files and rendering those on screen, as well as a
comprehensive API for recording audio and video from the systems cameras and
microphones.

The functionality of this module is divided into the following submodules:


    +---------------------------------------------------+-----------------------------------------------+
    |:ref:`Qt Multimedia<Multimedia-Overview>`          |Provides API for multimedia-specific use cases.|
    +---------------------------------------------------+-----------------------------------------------+
    |:ref:`Qt Multimedia Widgets<Qt-Multimedia-Widgets>`|Provides the widget-based multimedia API.      |
    +---------------------------------------------------+-----------------------------------------------+

Getting started
^^^^^^^^^^^^^^^

If you are porting from Qt 5 to Qt 6 see :ref:`Changes to Qt Multimedia<Changes-to-Qt-Multimedia>` .

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtMultimedia

The module also provides `QML types <https://doc.qt.io/qt-6/qtmultimedia-qmlmodule.html>`_ .

Overviews and Important Topics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * :ref:`Changes in Qt 6<Changes-to-Qt-Multimedia>`
    * :ref:`Multimedia Overview<Multimedia-Overview>`
    * :ref:`Audio Overview<Audio-Overview>`
    * :ref:`Video Overview<Video-Overview>`
    * :ref:`Camera Overview<Camera-Overview>`
    * :ref:`Supported Media Formats<Video-Overview>`

QML Types
^^^^^^^^^

The following table outlines some important QML types.

    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |Type                                                                           |Description                                                                                                                                                                                                                                             |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`MediaPlayer <https://doc.qt.io/qt-6/qml-qtmultimedia-mediaplayer.html>`_      |Add audio/video playback functionality to a scene.                                                                                                                                                                                                      |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`CaptureSession <https://doc.qt.io/qt-6/qml-qtmultimedia-capturesession.html>`_|Create a session for capturing audio/video.                                                                                                                                                                                                             |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`Camera <https://doc.qt.io/qt-6/qml-qtmultimedia-camera.html>`_                |Access a camera connected to the system.                                                                                                                                                                                                                |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`AudioInput <https://doc.qt.io/qt-6/qml-qtmultimedia-audioinput.html>`_        |Access an audio input (microphone) connected to the system.                                                                                                                                                                                             |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`AudioOutput <https://doc.qt.io/qt-6/qml-qtmultimedia-audiooutput.html>`_      |Access an audio output (speaker, headphone) connected to the system.                                                                                                                                                                                    |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`VideoOutput <https://doc.qt.io/qt-6/qml-qtmultimedia-videooutput.html>`_      |Display video content.                                                                                                                                                                                                                                  |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`MediaRecorder <https://doc.qt.io/qt-6/qml-qtmultimedia-mediarecorder.html>`_  |Record audio/video from the `CaptureSession <https://doc.qt.io/qt-6/qml-qtmultimedia-capturesession.html>`_ .                                                                                                                                           |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`ImageCapture <https://doc.qt.io/qt-6/qml-qtmultimedia-imagecapture.html>`_    |Capture still images from the Camera.                                                                                                                                                                                                                   |
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |`Video <https://doc.qt.io/qt-6/qml-qtmultimedia-video.html>`_                  |Add Video playback functionality to a scene. Uses `MediaPlayer <https://doc.qt.io/qt-6/qml-qtmultimedia-mediaplayer.html>`_ and `VideoOutput <https://doc.qt.io/qt-6/qml-qtmultimedia-videooutput.html>`_ types to provide video playback functionality.|
    +-------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

C++ Classes
^^^^^^^^^^^

The following table outlines some important C++ Classes

    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |Class                                                                   |Description                                                         |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QMediaPlayer<PySide6.QtMultimedia.QMediaPlayer>`                |Playback media from a source.                                       |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QVideoWidget<PySide6.QtMultimediaWidgets.QVideoWidget>`         |Display video from a media player or a capture session.             |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QMediaCaptureSession<PySide6.QtMultimedia.QMediaCaptureSession>`|Capture audio and video.                                            |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QCamera<PySide6.QtMultimedia.QCamera>`                          |Access a camera connected to the system                             |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QAudioInput<PySide6.QtMultimedia.QAudioInput>`                  |Access an audio input (microphone) connected to the system.         |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QAudioOutput<PySide6.QtMultimedia.QAudioOutput>`                |Access an audio output (speaker, headphone) connected to the system.|
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QImageCapture<PySide6.QtMultimedia.QImageCapture>`              |Capture still images with a camera.                                 |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QMediaRecorder<PySide6.QtMultimedia.QMediaRecorder>`            |Record media content from a capture session.                        |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QVideoSink<PySide6.QtMultimedia.QVideoSink>`                    |Access and render individual video frames.                          |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+
    |:class:`QAudioSink<PySide6.QtMultimedia.QAudioSink>`                    |Sends raw audio data to an audio output device.                     |
    +------------------------------------------------------------------------+--------------------------------------------------------------------+

For playback :class:`QMediaPlayer<PySide6.QtMultimedia.QMediaPlayer>` ,
:class:`QAudioOutput<PySide6.QtMultimedia.QAudioOutput>` and QVideoOutput
contain all the required functionality. The other classes are used for
capturing audio and video content, where the
:class:`QMediaCaptureSession<PySide6.QtMultimedia.QMediaCaptureSession>` is the
central class managing the whole capture/recording process.
