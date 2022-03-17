cmake_minimum_required(VERSION 3.16)

# Standalone-buildable

project(qtxmltosphinx)

set(CMAKE_AUTOMOC ON)

find_package(Qt6 COMPONENTS Core)

set(generator_src_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../generator)
set(api_extractor_src_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../ApiExtractor)

set(qtxmltosphinx_SRC
    ${generator_src_dir}/qtdoc/qtxmltosphinx.cpp
    ${api_extractor_src_dir}/codesniphelpers.cpp
    ${api_extractor_src_dir}/textstream.cpp
    main.cpp)

add_executable(qtxmltosphinx ${qtxmltosphinx_SRC})

target_include_directories(qtxmltosphinx PRIVATE
                           ${CMAKE_CURRENT_BINARY_DIR}
                           ${api_extractor_src_dir}
                           ${generator_src_dir}
                           ${generator_src_dir}/shiboken
                           ${generator_src_dir}/qtdoc)

target_link_libraries(qtxmltosphinx PRIVATE Qt::Core)
