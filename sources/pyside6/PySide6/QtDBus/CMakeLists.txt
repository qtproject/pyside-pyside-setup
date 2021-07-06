project(QtDBus)

set(QtDBus_SRC
    ${QtDBus_GEN_DIR}/qdbus_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusabstractadaptor_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusabstractinterface_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusabstractinterfacebase_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusargument_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusconnection_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusconnectioninterface_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbuscontext_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbuserror_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusinterface_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusmessage_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusobjectpath_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbuspendingcall_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbuspendingcallwatcher_wrapper.cpp
    ${QtDBus_GEN_DIR}/qtdbushelper_qdbusreply_wrapper.cpp
    #${QtDBus_GEN_DIR}/qdbuspendingreply_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusserver_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusservicewatcher_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbussignature_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusunixfiledescriptor_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusvariant_wrapper.cpp
    ${QtDBus_GEN_DIR}/qdbusvirtualobject_wrapper.cpp
# module is always needed
    ${QtDBus_GEN_DIR}/qtdbus_module_wrapper.cpp
)

configure_file("${QtDBus_SOURCE_DIR}/QtDBus_global.post.h.in"
               "${QtDBus_BINARY_DIR}/QtDBus_global.post.h" @ONLY)

set(QtDBus_include_dirs ${QtDBus_SOURCE_DIR}
                        ${QtDBus_BINARY_DIR}
                        ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                        ${Qt${QT_MAJOR_VERSION}DBus_INCLUDE_DIRS}
                        ${libpyside_SOURCE_DIR}
                        ${QtCore_GEN_DIR})

set(QtDBus_libraries pyside6 ${Qt${QT_MAJOR_VERSION}DBus_LIBRARIES})

set(QtDBus_deps QtCore)

create_pyside_module(NAME QtDBus
                     INCLUDE_DIRS QtDBus_include_dirs
                     LIBRARIES QtDBus_libraries
                     DEPS QtDBus_deps
                     TYPESYSTEM_PATH QtDBus_SOURCE_DIR
                     SOURCES QtDBus_SRC)

install(FILES ${pyside6_SOURCE_DIR}/qtdbushelper.h DESTINATION include/PySide6/QtDBus)
