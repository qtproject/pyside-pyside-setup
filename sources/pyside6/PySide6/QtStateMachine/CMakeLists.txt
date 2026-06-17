# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(QtStateMachine)

set(QtStateMachine_SRC
${QtStateMachine_GEN_DIR}/qabstractstate_wrapper.cpp
${QtStateMachine_GEN_DIR}/qabstracttransition_wrapper.cpp
${QtStateMachine_GEN_DIR}/qeventtransition_wrapper.cpp
${QtStateMachine_GEN_DIR}/qkeyeventtransition_wrapper.cpp
${QtStateMachine_GEN_DIR}/qmouseeventtransition_wrapper.cpp
${QtStateMachine_GEN_DIR}/qfinalstate_wrapper.cpp
${QtStateMachine_GEN_DIR}/qhistorystate_wrapper.cpp
${QtStateMachine_GEN_DIR}/qsignaltransition_wrapper.cpp
${QtStateMachine_GEN_DIR}/qstate_wrapper.cpp
${QtStateMachine_GEN_DIR}/qstatemachine_wrapper.cpp
${QtStateMachine_GEN_DIR}/qstatemachine_signalevent_wrapper.cpp
${QtStateMachine_GEN_DIR}/qstatemachine_wrappedevent_wrapper.cpp
# module is always needed
${QtStateMachine_GEN_DIR}/qtstatemachine_module_wrapper.cpp
)

set(QtStateMachine_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
)

set(QtStateMachine_deps
    QtGui
)

set(QtStateMachine_libraries
    Qt::StateMachine
)

create_pyside_module(NAME QtStateMachine
                     INCLUDE_DIRS QtStateMachine_include_dirs
                     LIBRARIES QtStateMachine_libraries
                     DEPS QtStateMachine_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtStateMachine_SRC
                     TYPESYSTEM_NAME "${CMAKE_CURRENT_BINARY_DIR}/typesystem_statemachine.xml")
