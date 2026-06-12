# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtMultimedia_SRC
${QtMultimedia_GEN_DIR}/qabstractvideobuffer_wrapper.cpp
${QtMultimedia_GEN_DIR}/qabstractvideobuffer_mapdata_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiobuffer_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiobufferinput_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiobufferoutput_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiodecoder_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiodevice_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudioformat_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudioinput_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiooutput_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiosink_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudiosource_wrapper.cpp
${QtMultimedia_GEN_DIR}/qaudio_wrapper.cpp
${QtMultimedia_GEN_DIR}/qcameraformat_wrapper.cpp
${QtMultimedia_GEN_DIR}/qcameradevice_wrapper.cpp
${QtMultimedia_GEN_DIR}/qcamera_wrapper.cpp
${QtMultimedia_GEN_DIR}/qcapturablewindow_wrapper.cpp
${QtMultimedia_GEN_DIR}/qimagecapture_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediacapturesession_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediadevices_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediaformat_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediametadata_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediaplayer_wrapper.cpp
# ${QtMultimedia_GEN_DIR}/qmediaplaylist_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediarecorder_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediatimerange_wrapper.cpp
${QtMultimedia_GEN_DIR}/qmediatimerange_interval_wrapper.cpp
${QtMultimedia_GEN_DIR}/qplaybackoptions_wrapper.cpp
${QtMultimedia_GEN_DIR}/qscreencapture_wrapper.cpp
${QtMultimedia_GEN_DIR}/qsoundeffect_wrapper.cpp
${QtMultimedia_GEN_DIR}/qtaudio_wrapper.cpp
${QtMultimedia_GEN_DIR}/qtvideo_wrapper.cpp
${QtMultimedia_GEN_DIR}/qvideoframe_paintoptions_wrapper.cpp
${QtMultimedia_GEN_DIR}/qvideoframe_wrapper.cpp
${QtMultimedia_GEN_DIR}/qvideoframeformat_wrapper.cpp
${QtMultimedia_GEN_DIR}/qvideoframeinput_wrapper.cpp
${QtMultimedia_GEN_DIR}/qvideosink_wrapper.cpp
${QtMultimedia_GEN_DIR}/qwavedecoder_wrapper.cpp
${QtMultimedia_GEN_DIR}/qwindowcapture_wrapper.cpp

# module is always needed
${QtMultimedia_GEN_DIR}/qtmultimedia_module_wrapper.cpp
)

set(QtMultimedia_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtNetwork_GEN_DIR}
)

set(QtMultimedia_deps
    QtCore
    QtGui
    QtNetwork
)

set(QtMultimedia_libraries
    Qt::Multimedia
)

create_pyside_module(NAME QtMultimedia
                     INCLUDE_DIRS QtMultimedia_include_dirs
                     LIBRARIES QtMultimedia_libraries
                     DEPS QtMultimedia_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtMultimedia_SRC)
