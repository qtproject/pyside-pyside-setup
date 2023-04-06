# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
# python missing_bindings.py --qt-version 6.3 -w all
# --qt-version - specify which version of qt documentation to load.
# -w           - if PyQt6 is an installed package, check if the tested
# class also exists there.

import argparse
import sys
from textwrap import dedent
from time import gmtime, strftime
from urllib import request
from pathlib import Path

from bs4 import BeautifulSoup
from config import modules_to_test, types_to_ignore
import pandas as pd
import matplotlib.pyplot as plt

qt_documentation_website_prefixes = {
    "6.5": "https://doc.qt.io/qt-6/",
    "dev": "https://doc-snapshots.qt.io/qt6-dev/",
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
        default="6.5",
        choices=["6.5", "dev"],
        type=str,
        dest="version",
        help="the Qt version to use to check for types",
    )
    parser.add_argument(
        "--which-missing",
        "-w",
        default="all",
        choices=["all", "in-pyqt", "not-in-pyqt", "in-pyside-not-in-pyqt"],
        type=str,
        dest="which_missing",
        help="Which missing types to show (all, or just those that are not present in PyQt)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Create module-wise bar plot comparisons for the missing bindings comparisons"
             " between Qt, PySide6 and PyQt6",
    )
    return parser


def wikilog(*pargs, **kw):
    print(*pargs)

    computed_str = "".join(str(arg) for arg in pargs)

    style = "text"
    if "style" in kw:
        style = kw["style"]

    if style == "heading1":
        computed_str = f"= {computed_str} ="
    elif style == "heading5":
        computed_str = f"===== {computed_str} ====="
    elif style == "with_newline":
        computed_str = f"{computed_str}\n"
    elif style == "bold_colon":
        computed_str = computed_str.replace(":", ":'''")
        computed_str = f"{computed_str}'''\n"
    elif style == "error":
        computed_str = computed_str.strip("\n")
        computed_str = f"''{computed_str}''\n"
    elif style == "text_with_link":
        computed_str = computed_str
    elif style == "code":
        computed_str = f" {computed_str}"
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

    data = {"module": [], "qt": [], "pyside": [], "pyqt": []}
    total_missing_types_count = 0
    total_missing_types_count_compared_to_pyqt = 0
    total_missing_modules_count = 0
    total_missing_pyqt_types_count = 0
    total_missing_pyqt_modules_count = 0

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
        "Similar report:\n https://gist.github.com/ethanhs/6c626ca4e291f3682589699296377d3a",
        style="text_with_link",
    )

    python_executable = Path(sys.executable).name or ""
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
            total_missing_pyqt_modules_count += 1

        # Get C++ class list from documentation page.
        page = request.urlopen(url)
        soup = BeautifulSoup(page, "html.parser")

        #  Extract the Qt type names from the documentation classes table
        links = soup.body.select(".annotated a")
        types_on_html_page = []

        for link in links:
            link_text = link.text.replace("::", ".")
            if link_text not in types_to_ignore:
                types_on_html_page.append(link_text)

        total_qt_types = len(types_on_html_page)
        wikilog(f"Number of types in {module_name}: {total_qt_types}", style="bold_colon")

        missing_pyside_types_count = 0
        missing_pyqt_types_count = 0
        missing_types_compared_to_pyqt = 0
        missing_types = []
        for qt_type in types_on_html_page:
            is_present_in_pyqt = False
            is_present_in_pyside = False
            missing_type = None

            try:
                pyqt_qualified_type = f"pyqt_tested_module.{qt_type}"
                eval(pyqt_qualified_type)
                is_present_in_pyqt = True
            except Exception as e:
                print(f"{type(e).__name__}: {e}")
                missing_pyqt_types_count += 1
                total_missing_pyqt_types_count += 1

            try:
                pyside_qualified_type = f"pyside_tested_module.{qt_type}"
                eval(pyside_qualified_type)
                is_present_in_pyside = True
            except Exception as e:
                print("Failed eval-in pyside qualified types")
                print(f"{type(e).__name__}: {e}")
                missing_type = qt_type
                missing_pyside_types_count += 1
                total_missing_types_count += 1

                if is_present_in_pyqt:
                    missing_type = f"{missing_type} (is present in PyQt6)"
                    missing_types_compared_to_pyqt += 1
                    total_missing_types_count_compared_to_pyqt += 1

            # missing in PySide
            if not is_present_in_pyside:
                if args.which_missing == "all":
                    missing_types.append(missing_type)
                    message = f"Missing types in PySide (all) {module_name}:"
                # missing in PySide and present in pyqt
                elif args.which_missing == "in-pyqt" and is_present_in_pyqt:
                    missing_types.append(missing_type)
                    message = f"Missing types in PySide6 (but present in PyQt6) {module_name}:"
                # missing in both PyQt and PySide
                elif args.which_missing == "not-in-pyqt" and not is_present_in_pyqt:
                    missing_types.append(missing_type)
                    message = f"Missing types in PySide6 (also missing in PyQt6) {module_name}:"
            elif (
                args.which_missing == "in-pyside-not-in-pyqt"
                and not is_present_in_pyqt
            ):
                missing_types.append(qt_type)
                message = f"Missing types in PyQt6 (but present in PySide6) {module_name}:"

        if len(missing_types) > 0:
            wikilog(message, style="with_newline")
            missing_types.sort()
            for missing_type in missing_types:
                wikilog(missing_type, style="code")
            wikilog("")

        if args.which_missing != "in-pyside-not-in-pyqt":
            missing_types_count = missing_pyside_types_count
        else:
            missing_types_count = missing_pyqt_types_count

        if args.plot:
            total_pyside_types = total_qt_types - missing_pyside_types_count
            total_pyqt_types = total_qt_types - missing_pyqt_types_count
            data["module"].append(module_name)
            data["qt"].append(total_qt_types)
            data["pyside"].append(total_pyside_types)
            data["pyqt"].append(total_pyqt_types)

        wikilog(f"Number of missing types: {missing_types_count}", style="bold_colon")
        if len(missing_types) > 0 and args.which_missing != "in-pyside-not-in-pyqt":
            wikilog(
                "Number of missing types that are present in PyQt6: "
                f"{missing_types_compared_to_pyqt}",
                style="bold_colon",
            )
            wikilog(f"End of missing types for {module_name}\n", style="end")
        else:
            wikilog("", style="end")

    if args.plot:
        df = pd.DataFrame(data=data, columns=["module", "qt", "pyside", "pyqt"])
        df.set_index("module", inplace=True)
        df.plot(kind="bar", title="Qt API Coverage plot")
        plt.legend()
        plt.xticks(rotation=45)
        plt.ylabel("Types Count")
        figure = plt.gcf()
        figure.set_size_inches(32, 18) # set to full_screen
        plt.savefig("missing_bindings_comparison_plot.png", bbox_inches='tight')
        print(f"Plot saved in {Path.cwd() / 'missing_bindings_comparison_plot.png'}\n")

    wikilog("Summary", style="heading5")

    if args.which_missing != "in-pyside-not-in-pyqt":
        wikilog(f"Total number of missing types: {total_missing_types_count}", style="bold_colon")
        wikilog(
            "Total number of missing types that are present in PyQt6: "
            f"{total_missing_types_count_compared_to_pyqt}",
            style="bold_colon",
        )
        wikilog(
            f"Total number of missing modules: {total_missing_modules_count}", style="bold_colon"
        )
    else:
        wikilog(
            f"Total number of missing types in PyQt6: {total_missing_pyqt_types_count}",
            style="bold_colon",
        )
        wikilog(
            f"Total number of missing modules in PyQt6: {total_missing_pyqt_modules_count}",
            style="bold_colon",
        )
    wiki_file.close()
