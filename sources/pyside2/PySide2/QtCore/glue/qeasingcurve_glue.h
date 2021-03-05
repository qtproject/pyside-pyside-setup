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

#ifndef __QEASINGCURVE_GLUE__
#define __QEASINGCURVE_GLUE__

#include <sbkpython.h>
#include <QEasingCurve>

class PySideEasingCurveFunctor
{
    public:
        static void init();
        static QEasingCurve::EasingFunction createCustomFuntion(PyObject *parent, PyObject *pyFunc);

        qreal operator()(qreal progress);

        PyObject *callable(); //Return New reference
        static PyObject *callable(PyObject *parent); //Return New reference

        ~PySideEasingCurveFunctor();
    private:
        PyObject *m_parent;
        PyObject *m_func;
        int m_index;

        PySideEasingCurveFunctor(int index, PyObject *parent, PyObject *pyFunc);
};

#endif
