cmake_minimum_required(VERSION 3.25)

# dumpcodemodel depends on apiextractor which is not cross-built.
add_subdirectory(dumpcodemodel)

if (NOT APIEXTRACTOR_DOCSTRINGS_DISABLED)
    add_subdirectory(qtxmltosphinxtest)
endif()
