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

// @snippet releaseownership
Shiboken::Object::releaseOwnership(%PYARG_1);
// @snippet releaseownership

// @snippet qcustom3dvolume-settexturedata
using VectorType = decltype(%1);
%CPPSELF.setTextureData(new VectorType(%1));
// @snippet qcustom3dvolume-settexturedata

// @snippet dataproxy-addrow
using VectorType = decltype(%1);
%RETURN_TYPE %0 = %CPPSELF.addRow(new VectorType(%1));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet dataproxy-addrow

// @snippet dataproxy-addrow-string
using VectorType = decltype(%1);
%RETURN_TYPE %0 = %CPPSELF.addRow(new VectorType(%1), %2);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet dataproxy-addrow-string

// @snippet dataproxy-insertrow
using VectorType = decltype(%2);
%CPPSELF.insertRow(%1, new VectorType(%2));
// @snippet dataproxy-insertrow

// @snippet dataproxy-insertrow-string
using VectorType = decltype(%2);
%CPPSELF.insertRow(%1, new VectorType(%2), %3);
// @snippet dataproxy-insertrow-string

// @snippet dataproxy-setrow
using VectorType = decltype(%2);
%CPPSELF.setRow(%1, new VectorType(%2));
// @snippet dataproxy-setrow

// @snippet dataproxy-setrow-string
using VectorType = decltype(%2);
%CPPSELF.setRow(%1, new VectorType(%2), %3);
// @snippet dataproxy-setrow-string
