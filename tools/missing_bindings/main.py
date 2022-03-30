#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

# This script is used to generate a summary of missing types / classes
# which are present in C++ Qt6, but are missing in PySide6.
#
# Required packages: bs4
# Installed via: pip install bs4
#
# The script uses beautiful soup 4 to parse out the class names from
# the online Qt documentation. It then tries to import the types from
# PySide6.
#
# Example invocation of script:
# python missing_bindings.py --qt-version 6.0 -w all
# --qt-version - specify which version of qt documentation to load.
# -w           - if PyQt6 is an installed package, check if the tested
# class also exists there.

import argparse
import os.path
import sys
from textwrap import dedent
from time import gmtime, strftime
from urllib import request

from bs4 import BeautifulSoup

from config import modules_to_test, types_to_ignore

qt_documentation_website_prefixes = {
    "6.0": "https://doc.qt.io/qt-6/",
    "dev": "https://doc-snapshots.qt.io/qt5-dev/",
}


def qt_version_to_doc_prefix(version):
    if version in qt_documentation_website_prefixes:
        return qt_documentation_website_prefixes[version]
    else:
        raise RuntimeError("The specified qt version is not supported")


def create_doc_url(module_doc_page_url, version):
    return qt_version_to_doc_prefix(version) + module_doc_page_url


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "module",
        default="all",
        choices=list(modules_to_test.keys()).append("all"),
        nargs="?",
        type=str,
        help="the Qt module for which to get the missing types",
    )
    parser.add_argument(
        "--qt-version",
        "-v",
        default="6.0",
        choices=["6.0", "dev"],
        type=str,
        dest="version",
        help="the Qt version to use to check for types",
    )
    parser.add_argument(
        "--which-missing",
        "-w",
        default="all",
        choices=["all", "in-pyqt", "not-in-pyqt"],
        type=str,
        dest="which_missing",
        help="Which missing types to show (all, or just those " "that are not present in PyQt)",
    )
    return parser


def wikilog(*pargs, **kw):
    print(*pargs)

    computed_str = ""
    for arg in pargs:
        computed_str += str(arg)

    style = "text"
    if "style" in kw:
        style = kw["style"]

    if style == "heading1":
        computed_str = "= " + computed_str + " ="
    elif style == "heading5":
        computed_str = "===== " + computed_str + " ====="
    elif style == "with_newline":
        computed_str += "\n"
    elif style == "bold_colon":
        computed_str = computed_str.replace(":", ":'''")
        computed_str += "'''"
        computed_str += "\n"
    elif style == "error":
        computed_str = "''" + computed_str.strip("\n") + "''\n"
    elif style == "text_with_link":
        computed_str = computed_str
    elif style == "code":
        computed_str = " " + computed_str
    elif style == "end":
        return

    print(computed_str, file=wiki_file)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if hasattr(args, "module") and args.module != "all":
        saved_value = modules_to_test[args.module]
        modules_to_test.clear()
        modules_to_test[args.module] = saved_value

    pyside_package_name = "PySide6"
    pyqt_package_name = "PyQt6"

    total_missing_types_count = 0
    total_missing_types_count_compared_to_pyqt = 0
    total_missing_modules_count = 0

    wiki_file = open("missing_bindings_for_wiki_qt_io.txt", "w")
    wiki_file.truncate()

    wikilog(f"PySide6 bindings for Qt {args.version}", style="heading1")

    wikilog(
        f"Using Qt version {args.version} documentation to find public "
        "API Qt types and test if the types are present in the PySide6 "
        "package."
    )

    wikilog(
        dedent(
            """\
        Results are usually stored at
            https://wiki.qt.io/PySide6_Missing_Bindings
        so consider taking the contents of the generated
            missing_bindings_for_wiki_qt_io.txt
        file and updating the linked wiki page."""
        ),
        style="end",
    )

    wikilog(
        "Similar report:\n" "https://gist.github.com/ethanhs/6c626ca4e291f3682589699296377d3a",
        style="text_with_link",
    )

    python_executable = os.path.basename(sys.executable or "")
    command_line_arguments = " ".join(sys.argv)
    report_date = strftime("%Y-%m-%d %H:%M:%S %Z", gmtime())

    wikilog(
        dedent(
            f"""
    This report was generated by running the following command:
     {python_executable} {command_line_arguments}
    on the following date:
     {report_date}
    """
        )
    )

    for module_name in modules_to_test.keys():
        wikilog(module_name, style="heading5")

        url = create_doc_url(modules_to_test[module_name], args.version)
        wikilog(f"Documentation link: {url}\n", style="text_with_link")

        # Import the tested module
        try:
            pyside_tested_module = getattr(
                __import__(pyside_package_name, fromlist=[module_name]), module_name
            )
        except Exception as e:
            e_str = str(e).replace('"', "")
            wikilog(
                f"\nCould not load {pyside_package_name}.{module_name}. "
                f"Received error: {e_str}. Skipping.\n",
                style="error",
            )
            total_missing_modules_count += 1
            continue

        try:
            pyqt_module_name = module_name
            if module_name == "QtCharts":
                pyqt_module_name = module_name[:-1]

            pyqt_tested_module = getattr(
                __import__(pyqt_package_name, fromlist=[pyqt_module_name]), pyqt_module_name
            )
        except Exception as e:
            e_str = str(e).replace("'", "")
            wikilog(
                f"\nCould not load {pyqt_package_name}.{module_name} for comparison. "
                f"Received error: {e_str}.\n",
                style="error",
            )

        # Get C++ class list from documentation page.
        page = request.urlopen(url)
        soup = BeautifulSoup(page, "html.parser")

        #  Extract the Qt type names from the documentation classes table
        links = soup.body.select(".annotated a")
        types_on_html_page = []

        for link in links:
            link_text = link.text
            link_text = link_text.replace("::", ".")
            if link_text not in types_to_ignore:
                types_on_html_page.append(link_text)

        wikilog(f"Number of types in {module_name}: {len(types_on_html_page)}", style="bold_colon")

        missing_types_count = 0
        missing_types_compared_to_pyqt = 0
        missing_types = []
        for qt_type in types_on_html_page:
            try:
                pyside_qualified_type = "pyside_tested_module."

                if "QtCharts" == module_name:
                    pyside_qualified_type += "QtCharts."
                elif "DataVisualization" in module_name:
                    pyside_qualified_type += "QtDataVisualization."

                pyside_qualified_type += qt_type
                eval(pyside_qualified_type)
            except:
                missing_type = qt_type
                missing_types_count += 1
                total_missing_types_count += 1

                is_present_in_pyqt = False
                try:
                    pyqt_qualified_type = "pyqt_tested_module."

                    if "Charts" in module_name:
                        pyqt_qualified_type += "QtCharts."
                    elif "DataVisualization" in module_name:
                        pyqt_qualified_type += "QtDataVisualization."

                    pyqt_qualified_type += qt_type
                    eval(pyqt_qualified_type)
                    missing_type += " (is present in PyQt6)"
                    missing_types_compared_to_pyqt += 1
                    total_missing_types_count_compared_to_pyqt += 1
                    is_present_in_pyqt = True
                except:
                    pass

                if args.which_missing == "all":
                    missing_types.append(missing_type)
                elif args.which_missing == "in-pyqt" and is_present_in_pyqt:
                    missing_types.append(missing_type)
                elif args.which_missing == "not-in-pyqt" and not is_present_in_pyqt:
                    missing_types.append(missing_type)

        if len(missing_types) > 0:
            wikilog(f"Missing types in {module_name}:", style="with_newline")
            missing_types.sort()
            for missing_type in missing_types:
                wikilog(missing_type, style="code")
            wikilog("")

        wikilog(f"Number of missing types: {missing_types_count}", style="bold_colon")
        if len(missing_types) > 0:
            wikilog(
                "Number of missing types that are present in PyQt6: "
                f"{missing_types_compared_to_pyqt}",
                style="bold_colon",
            )
            wikilog(f"End of missing types for {module_name}\n", style="end")
        else:
            wikilog("", style="end")

    wikilog("Summary", style="heading5")
    wikilog(f"Total number of missing types: {total_missing_types_count}", style="bold_colon")
    wikilog(
        "Total number of missing types that are present in PyQt6: "
        f"{total_missing_types_count_compared_to_pyqt}",
        style="bold_colon",
    )
    wikilog(f"Total number of missing modules: {total_missing_modules_count}", style="bold_colon")
    wiki_file.close()
