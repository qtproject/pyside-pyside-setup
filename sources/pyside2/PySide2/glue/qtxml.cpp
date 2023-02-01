/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

// @snippet qxmlentityresolver-resolveentity
QXmlInputSource *_qxmlinputsource_arg_ = nullptr;
%BEGIN_ALLOW_THREADS
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(%1, %2, _qxmlinputsource_arg_);
%END_ALLOW_THREADS
%PYARG_0 = PyTuple_New(2);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](%0));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QXmlInputSource *](_qxmlinputsource_arg_));
// @snippet qxmlentityresolver-resolveentity

// @snippet qdomdocument-setcontent
QString _errorMsg_;
int _errorLine_ = 0;
int _errorColumn_ = 0;
%BEGIN_ALLOW_THREADS
bool _ret_ = %CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, &_errorMsg_, &_errorLine_,
    &_errorColumn_);
%END_ALLOW_THREADS
%PYARG_0 = PyTuple_New(4);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[bool](_ret_));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QString](_errorMsg_));
PyTuple_SET_ITEM(%PYARG_0, 2, %CONVERTTOPYTHON[int](_errorLine_));
PyTuple_SET_ITEM(%PYARG_0, 3, %CONVERTTOPYTHON[int](_errorColumn_));
// @snippet qdomdocument-setcontent
