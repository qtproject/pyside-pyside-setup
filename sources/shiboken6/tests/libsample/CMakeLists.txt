# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(libsample)

set(libsample_SRC
abstract.cpp abstract.h
blackbox.cpp blackbox.h
bucket.cpp bucket.h
bytearray.cpp bytearray.h
collector.cpp collector.h
complex.cpp complex.h
ctorconvrule.h
ctparam.cpp ctparam.h
cvlist.h
derived.cpp derived.h
derivedusingct.cpp derivedusingct.h
echo.cpp echo.h
exceptiontest.cpp exceptiontest.h
expression.cpp expression.h
filter.cpp filter.h
functions.cpp functions.h
handle.cpp handle.h
implicitconv.cpp implicitconv.h
injectcode.cpp injectcode.h
intwrapper.cpp intwrapper.h
libsamplemacros.h
list.h
listuser.cpp listuser.h
mapuser.cpp mapuser.h
modelindex.h
modifications.cpp modifications.h
modified_constructor.cpp modified_constructor.h
multiple_derived.cpp multiple_derived.h
noimplicitconversion.h
nondefaultctor.h
nontypetemplate.h
null.h
objectmodel.cpp objectmodel.h
objecttype.cpp objecttype.h
objecttypebyvalue.h
objecttypeholder.cpp objecttypeholder.h
objecttypelayout.cpp objecttypelayout.h
objecttypeoperators.cpp objecttypeoperators.h
objectview.cpp objectview.h
oddbool.cpp oddbool.h
onlycopy.cpp onlycopy.h
overload.cpp overload.h
overloadsort.cpp overloadsort.h
pairuser.cpp pairuser.h
pen.cpp pen.h
photon.cpp photon.h
point.cpp point.h
pointerholder.h
pointf.cpp pointf.h
polygon.cpp polygon.h
privatector.h
privatedtor.h
protected.cpp protected.h
rect.h
reference.cpp reference.h
removednamespaces.h
renaming.cpp renaming.h
sample.cpp sample.h
samplenamespace.cpp samplenamespace.h
sbkdate.cpp sbkdate.h
simplefile.cpp simplefile.h
size.cpp size.h
snakecasetest.cpp snakecasetest.h
sometime.cpp sometime.h
str.cpp str.h
strlist.cpp strlist.h
templateptr.cpp templateptr.h
transform.cpp transform.h
typesystypedef.cpp typesystypedef.h
valueandvirtual.h
virtualmethods.cpp virtualmethods.h
voidholder.h
)

add_library(libsample SHARED ${libsample_SRC})
target_include_directories(libsample PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_definitions(libsample PRIVATE LIBSAMPLE_BUILD)
set_property(TARGET libsample PROPERTY PREFIX "")

