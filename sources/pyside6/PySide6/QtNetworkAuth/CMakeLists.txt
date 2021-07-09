project(QtNetworkAuth)

set(QtNetworkAuth_SRC
${QtNetworkAuth_GEN_DIR}/qabstractoauth_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qabstractoauth2_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qabstractoauthreplyhandler_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauth1_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauth1signature_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauth2authorizationcodeflow_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauthhttpserverreplyhandler_wrapper.cpp
${QtNetworkAuth_GEN_DIR}/qoauthoobreplyhandler_wrapper.cpp
# module is always needed
${QtNetworkAuth_GEN_DIR}/qtnetworkauth_module_wrapper.cpp
)

set(QtNetworkAuth_include_dirs ${QtNetworkAuth_SOURCE_DIR}
                               ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                               ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                               ${Qt${QT_MAJOR_VERSION}NetworkAuth_INCLUDE_DIRS}
                               ${libpyside_SOURCE_DIR}
                               ${QtCore_GEN_DIR}
                               ${QtNetwork_GEN_DIR}
                               ${QtNetworkAuth_GEN_DIR})

set(QtNetworkAuth_libraries pyside6
                            ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}NetworkAuth_LIBRARIES})

set(QtNetworkAuth_deps QtNetwork)

create_pyside_module(NAME QtNetworkAuth
                     INCLUDE_DIRS QtNetworkAuth_include_dirs
                     LIBRARIES QtNetworkAuth_libraries
                     DEPS QtNetworkAuth_deps
                     TYPESYSTEM_PATH QtNetworkAuth_SOURCE_DIR
                     SOURCES QtNetworkAuth_SRC)
