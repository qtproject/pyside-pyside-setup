# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(sample)

set(sample_TYPESYSTEM
${CMAKE_CURRENT_SOURCE_DIR}/typesystem_sample.xml
)

set(sample_SRC
${CMAKE_CURRENT_BINARY_DIR}/sample/abstractmodifications_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/abstract_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/arraymodifytest_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/base1_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/base2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/base3_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/base4_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/base5_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/base6_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/blackbox_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/brush_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/bytearray_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/bucket_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/classwithfunctionpointer_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/collector_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/comparisontester_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/color_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/ctorconvrule_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/customoverloadsequence_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/cvlistuser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/cvvaluetype_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/sbkdate_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/deleteddefaultctor_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/derived_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/derivedusingct_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/derived_someinnerclass_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/echo_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/event_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/expression_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/exceptiontest_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/friendofonlycopy_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/handleholder_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/implicitconv_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/implicitbase_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/implicittarget_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/intarray2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/intarray3_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/intlist_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/sortedoverload_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/intwrapper_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/injectcode_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/listuser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/mapuser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/mderived1_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/mderived2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/mderived3_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/mderived4_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/mderived5_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/modelindex_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/modifications_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/modifiedconstructor_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/noimplicitconversion_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/nondefaultctor_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objectmodel_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objecttype_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objecttypebyvalue_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objecttypeholder_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objecttypederived_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objecttypelayout_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objecttypeptrlist_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objecttypeoperators_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objectview_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/objtypereference_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/oddbooluser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/onlycopy_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/otherbase_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/overload_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/overload2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/pairuser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/pen_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/persistentmodelindex_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/photon_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/photon_base_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/photon_valueidentity_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/photon_valueduplicator_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/point_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/pointerholder_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/pointf_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/pointvaluelist_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/polygon_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/primitivestructpointerholder_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/privatector_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/privatedtor_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/protectedenumclass_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/protectednonpolymorphic_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/protectedpolymorphic_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/protectedpolymorphicdaughter_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/protectedpolymorphicgranddaughter_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/protectedproperty_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/protectedvirtualdestructor_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/rect_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/rectf_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/reference_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/referentmodelindex_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/toberenamedvalue_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/removednamespace1_objectoninvisiblenamespace_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/renameduser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/sample_module_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/sample_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/sample_sample_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_ctparam_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_inlinenamespace_classwithininlinenamespace_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_someclass_someinnerclass_okthisisrecursiveenough_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_someclass_someinnerclass_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_someclass_someotherinnerclass_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_someclass_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/samplenamespace_derivedfromnamespace_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/stdcomplex_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/simplefile_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/size_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/sizef_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/snakecasetest_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/snakecasederivedtest_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/sonofmderived1_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/spaceshipcomparisontester_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/str_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/strlist_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/time_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/templateptr_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/unremovednamespace_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/valuewithunitdoubleinch_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/valuewithunitdoublemillimeter_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/valuewithunituser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/virtualdaughter_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/virtualdaughter2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/virtualfinaldaughter_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/virtualdtor_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/virtualmethods_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/voidholder_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/valueandvirtual_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/filter_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/data_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/intersection_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/sample/union_wrapper.cpp
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/sample-binding.txt.in"
               "${CMAKE_CURRENT_BINARY_DIR}/sample-binding.txt" @ONLY)

shiboken_get_tool_shell_wrapper(shiboken tool_wrapper)

add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/mjb_rejected_classes.log"
    BYPRODUCTS ${sample_SRC}
    COMMAND
        ${tool_wrapper}
        $<TARGET_FILE:Shiboken6::shiboken6>
        --project-file=${CMAKE_CURRENT_BINARY_DIR}/sample-binding.txt
        ${GENERATOR_EXTRA_FLAGS}
    DEPENDS ${sample_TYPESYSTEM} ${CMAKE_CURRENT_SOURCE_DIR}/global.h Shiboken6::shiboken6
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running generator for 'sample' test binding..."
)

add_library(sample MODULE ${sample_SRC})
target_include_directories(sample PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(sample PUBLIC libsample libshiboken)
set_property(TARGET sample PROPERTY PREFIX "")
set_property(TARGET sample PROPERTY OUTPUT_NAME "sample${PYTHON_EXTENSION_SUFFIX}")

if(WIN32)
    set_property(TARGET sample PROPERTY SUFFIX ".pyd")
endif()

create_generator_target(sample)
