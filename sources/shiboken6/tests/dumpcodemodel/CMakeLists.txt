add_executable(dumpcodemodel main.cpp)

target_include_directories(dumpcodemodel
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/../../ApiExtractor
)

target_link_libraries(dumpcodemodel
    PRIVATE
        apiextractor
        Qt${QT_MAJOR_VERSION}::Core
)
