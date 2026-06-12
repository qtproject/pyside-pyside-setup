# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtSql_SRC
${QtSql_GEN_DIR}/qsql_wrapper.cpp
${QtSql_GEN_DIR}/qsqldatabase_wrapper.cpp
${QtSql_GEN_DIR}/qsqldriver_wrapper.cpp
${QtSql_GEN_DIR}/qsqldrivercreatorbase_wrapper.cpp
${QtSql_GEN_DIR}/qsqlerror_wrapper.cpp
${QtSql_GEN_DIR}/qsqlfield_wrapper.cpp
${QtSql_GEN_DIR}/qsqlindex_wrapper.cpp
${QtSql_GEN_DIR}/qsqlquery_wrapper.cpp
${QtSql_GEN_DIR}/qsqlquerymodel_wrapper.cpp
${QtSql_GEN_DIR}/qsqlrecord_wrapper.cpp
${QtSql_GEN_DIR}/qsqlrelation_wrapper.cpp
${QtSql_GEN_DIR}/qsqlrelationaldelegate_wrapper.cpp
${QtSql_GEN_DIR}/qsqlrelationaltablemodel_wrapper.cpp
${QtSql_GEN_DIR}/qsqlresult_wrapper.cpp
${QtSql_GEN_DIR}/qsqltablemodel_wrapper.cpp
# module is always needed
${QtSql_GEN_DIR}/qtsql_module_wrapper.cpp
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/QtSql_global.pre.h.in"
               "${CMAKE_CURRENT_BINARY_DIR}/QtSql_global.pre.h" @ONLY)

set(QtSql_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtWidgets_GEN_DIR}
)

set(QtSql_deps
    QtWidgets
)

# Link to QtWidgets to enable QSqlRelationalDelegate
set(QtSql_libraries
    Qt::Widgets
    Qt::Sql
)

create_pyside_module(NAME QtSql
                     INCLUDE_DIRS QtSql_include_dirs
                     LIBRARIES QtSql_libraries
                     DEPS QtSql_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtSql_SRC)
