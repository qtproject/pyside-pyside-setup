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

set(QtStateMachine_include_dirs  ${QtStateMachine_SOURCE_DIR}
                            ${QtStateMachine_BINARY_DIR}
                            ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                            ${libpyside_SOURCE_DIR}
                            ${QtCore_GEN_DIR}
                            ${QtGui_GEN_DIR}
                            )
set(QtStateMachine_libraries pyside6
                        ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                        ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
                        ${Qt${QT_MAJOR_VERSION}StateMachine_LIBRARIES}
                        )
set(QtStateMachine_deps QtGui)

create_pyside_module(NAME QtStateMachine
                     INCLUDE_DIRS QtStateMachine_include_dirs
                     LIBRARIES QtStateMachine_libraries
                     DEPS QtStateMachine_deps
                     TYPESYSTEM_PATH QtStateMachine_SOURCE_DIR
                     SOURCES QtStateMachine_SRC
                     TYPESYSTEM_NAME ${QtStateMachine_BINARY_DIR}/typesystem_statemachine.xml)
