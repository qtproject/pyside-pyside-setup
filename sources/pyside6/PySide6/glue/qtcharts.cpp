// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qchart-releaseownership
Shiboken::Object::releaseOwnership(%PYARG_1);
// @snippet qchart-releaseownership

// @snippet qxyseries-appendnp-numpy-x-y
const auto points = PySide::Numpy::xyDataToQPointFList(%PYARG_1, %PYARG_2);
%CPPSELF.append(points);
// @snippet qxyseries-appendnp-numpy-x-y

// @snippet qxyseries-replacenp-numpy-x-y
const auto points = PySide::Numpy::xyDataToQPointFList(%PYARG_1, %PYARG_2);
%CPPSELF.replace(points);
// @snippet qxyseries-replacenp-numpy-x-y
