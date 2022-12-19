// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OVERLOAD_H
#define OVERLOAD_H

#include "echo.h"
#include "str.h"
#include "size.h"
#include "point.h"
#include "pointf.h"
#include "polygon.h"
#include "rect.h"

#include "libsamplemacros.h"

class LIBSAMPLE_API Overload
{
public:
    enum FunctionEnum {
        Function0,
        Function1,
        Function2,
        Function3,
        Function4,
        Function5,
        Function6
    };

    enum ParamEnum {
        Param0,
        Param1
    };

    Overload() {}
    virtual ~Overload() {}

    FunctionEnum overloaded();
    FunctionEnum overloaded(Size *size);
    FunctionEnum overloaded(Point *point, ParamEnum param);
    FunctionEnum overloaded(const Point &point);

    void differentReturnTypes(ParamEnum param = Param0);
    int differentReturnTypes(ParamEnum param, int val);

    int intOverloads(const Point &p, double d);
    int intOverloads(int i, int i2);
    int intOverloads(int i, int removedArg, double d);

    FunctionEnum intDoubleOverloads(int a0, int a1) const;
    FunctionEnum intDoubleOverloads(double a0, double a1) const;

    void singleOverload(Point *x);
    Point *singleOverload() { return new Point(); }

    // Similar to QImage::trueMatrix(QMatrix,int,int) and QImage::trueMatrix(QTransform,int,int)
    FunctionEnum wrapperIntIntOverloads(const Point &arg0, int arg1, int arg2);
    FunctionEnum wrapperIntIntOverloads(const Polygon &arg0, int arg1, int arg2);

    // Similar to QImage constructor
    FunctionEnum strBufferOverloads(const Str &arg0, const char *arg1 = nullptr,
                                    bool arg2 = true);
    FunctionEnum strBufferOverloads(unsigned char *arg0, int arg1);
    FunctionEnum strBufferOverloads() { return Function2; }

    // Similar to QPainter::drawText(...)
    FunctionEnum drawText(const Point &a0, const Str &a1);
    FunctionEnum drawText(const PointF &a0, const Str &a1);
    FunctionEnum drawText(const Rect &a0, int a1, const Str &a2);
    FunctionEnum drawText(const RectF &a0, int a1, const Str &a2);
    FunctionEnum drawText(const RectF &a0, const Str &a1, const Echo &a2 = Echo());
    FunctionEnum drawText(int a0, int a1, const Str &a2);
    FunctionEnum drawText(int a0, int a1, int a2, int a3, int a4, const Str &a5);

    // A variant of the one similar to QPainter::drawText(...)
    FunctionEnum drawText2(const Point &a0, const Str &a1);
    FunctionEnum drawText2(const PointF &a0, const Str &a1);
    FunctionEnum drawText2(const Rect &a0, int a1, const Str &a2);
    FunctionEnum drawText2(const RectF &a0, int a1, const Str &a2);
    FunctionEnum drawText2(const RectF &a0, const Str &a1, const Echo &a2 = Echo());
    FunctionEnum drawText2(int a0, int a1, const Str &a2);
    FunctionEnum drawText2(int a0, int a1, int a2, int a3 = 0, int a4 = 0,
                           const Str &a5 = Str());

    // A simpler variant of the one similar to QPainter::drawText(...)
    FunctionEnum drawText3(const Str &a0, const Str &a1, const Str &a2);
    FunctionEnum drawText3(int a0, int a1, int a2, int a3, int a4);

    // Another simpler variant of the one similar to QPainter::drawText(...)
    FunctionEnum drawText4(int a0, int a1, int a2);
    FunctionEnum drawText4(int a0, int a1, int a2, int a3, int a4);

    FunctionEnum acceptSequence();
    FunctionEnum acceptSequence(int a0, int a1);
    FunctionEnum acceptSequence(const Str &a0, ParamEnum a1 = Param0);
    FunctionEnum acceptSequence(const Size &a0);
    // The type must be changed to PySequence.
    FunctionEnum acceptSequence(const char *const a0[]);
    FunctionEnum acceptSequence(void *a0);
};

class LIBSAMPLE_API Overload2 : public Overload
{
public:
    // test bug#616, public and private method differ only by const
    void doNothingInPublic() const {}
    void doNothingInPublic(int) {}
    virtual void doNothingInPublic3() const {}
    void doNothingInPublic3(int) const {}
protected:
    void doNothingInPublic2() const {}
    void doNothingInPublic2(int) {}
private:
    void doNothingInPublic() {}
    void doNothingInPublic2() {}
    void doNothingInPublic3() {}
};

#endif // OVERLOAD_H
