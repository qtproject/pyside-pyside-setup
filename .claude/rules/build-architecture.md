---
paths:
  - "build_scripts/**"
  - "sources/pyside-tools/**"
  - "sources/*/cmake/**"
  - "sources/**/*.in"
  - "CMakeLists.txt"
  - "**/CMakeLists.txt"
  - "**/*.cmake"
  - "**/*.cmake.in"
  - "create_wheels.py"
  - "setup.py"
  - "wheel_artifacts/**"
  - "build/**"
  - "build-super/**"
  - "tools/**"
---

# pyside-setup build architecture

How the PySide6 build pipeline is organized: source layout, the four
generated build trees, and the file-flow from `setup.py` to `.whl`.

## Top-level layout

- `setup.py` → `build_scripts/setup_runner.py` → CMake (per sub-project) → `create_wheels.py`.
- Root `CMakeLists.txt` is the *super-build* (used when building everything as one
  CMake project; the corresponding out-of-source tree is `build-super/`).
- `create_wheels.py` runs **after** the build, consuming `package_for_wheels/` plus
  templates in `wheel_artifacts/` (`pyproject.toml.base`, `setup.py.base`) to emit
  the 5–6 final wheels (`shiboken6`, `shiboken6_generator`, `PySide6_Essentials`,
  `PySide6_Addons`, `PySide6` meta, optional `PySide6_Examples`).
- `coin/` = Qt CI config (not shipped). `tools/` = repo maintenance scripts (not shipped).
  `testing/` = test runner. `examples/` = packaged into the Examples wheel.

## `sources/` - four sub-projects (built in this order)

The source tree separates the generator, its runtime, the generated bindings,
and the Python command-line tools. CMake configures each as a separate project.

### `shiboken6_generator/` - generate bindings from C++ headers

Builds the `shiboken6` executable. Its top-level CMake project builds the
following components in order:

- `ApiExtractor/` - static library that creates Shiboken's C++ and typesystem
  model. `apiextractor.*` coordinates parsing; `abstractmeta*` classes model
  C++ APIs; `typeentry` classes represent typesystem declarations;
  `typesystemparser.*`, `modifications.*`, `codesnip.*`, and
  `customconversion.*` read the XML binding rules. `clangparser/` uses
  libclang to parse Qt headers. `parser/` contains the legacy code model.
  `documentation.*`, `qtdocparser.*`, and `doxygenparser.*` add documentation
  when the XML/XSLT dependencies are available. The result is the common model
  consumed by every generator front-end.
- `generator/` - the executable front-end. `main.cpp` parses command-line
  options and drives extraction, while `generator.*`, `generatorcontext.*`,
  and `defaultvalue.*` provide shared generation machinery.
- `generator/shiboken/` - C++/Python binding front-end. It converts the
  extracted model and typesystem rules into module sources, one
  `*_wrapper.cpp/.h` pair per wrapped Qt class, plus module initialisation and
  converter code.
- `generator/qtdoc/` - documentation front-end. It converts the same model
  into the Sphinx `.rst` API documentation used by the PySide manual.
- `data/` - installed generator data, including default typesystem and support
  files needed when `shiboken6` runs outside the build tree.
- `cmake/` - CMake setup and find-module helpers for this sub-project.
- `doc/` and `tests/` - generator documentation and unit/integration tests.

### `shiboken6/` - runtime support for generated extensions

Builds the runtime that every generated PySide extension links against:

- `libshiboken/` - builds `libshiboken6.{so,dylib,dll}`. It manages Python/C++
  type registration, object identity and lifetime, Python-to-C++ converters,
  containers, enums, smart pointers, buffer support, signature metadata, and
  GIL/thread-state helpers.
- `shibokenmodule/` - builds the importable `Shiboken` Python extension and its
  generated `Shiboken.pyi` stub. It exposes diagnostic and support APIs backed
  by `libshiboken`.
- `data/` - installs headers, pkg-config metadata, manuals, and CMake package
  configuration so a downstream CMake project can use
  `find_package(Shiboken6)`.
- `cmake/` - CMake package configuration, compiler setup, and helper macros.
- `config.tests/` and `tests/` - feature probes and runtime test coverage.

### `pyside6/` - Qt bindings and PySide-specific libraries

Builds the PySide libraries and Python package. It first builds native support
libraries, then the generated Qt modules under `PySide6/`:

- `libpyside/` - builds `libpyside6`, the Qt/Python integration layer. It
  implements signals, slots, properties, dynamic `QMetaObject` support,
  `__feature__`, Python-backed Qt wrappers, and Qt-specific type helpers.
- `libpysideqml/` - builds `libpyside6qml` when Qt QML is available. Its
  `pysideqml*` and `pyside*` files implement QML registration, foreign and
  extended types, attached properties, auto-properties, computed properties,
  effects, watchers, list properties, and QML error handling.
- `PySide6/QtQmlFeatures/` - builds the `PySide6.QtQmlFeatures` extension and
  its `.pyi` file. The target source is
  `libpysideqml/pyside_feature_module.cpp`, so the package directory supplies
  build metadata while the implementation lives in `libpysideqml/`.
- `libpysideremoteobjects/` - small support library for the Qt Remote Objects
  bindings, built only when that Qt module is available.
- `PySide6/Qt<Module>/` - one directory for each generated Qt extension. Each
  provides `typesystem_<module>.xml`, common and platform-specific variants,
  parsed umbrella-header additions such as `Qt<Module>_global.post.h.in`, and
  `glue/` snippets referenced by `<inject-code>` entries. CMake passes these
  inputs to `shiboken6`, then compiles the generated wrapper sources into
  `PySide6.Qt<Module>`.
- `PySide6/support/` - the Python-side support package. `generate_pyi.py`
  imports built extension modules and writes their `.pyi` stubs;
  `qml_component_helper.py`, `auto_property_helper.py`, and `deprecated.py`
  provide runtime helpers.
- `PySide6/QtAsyncio/` - pure-Python Qt-aware `asyncio` event loop support.
- `PySide6/templates/` - reusable typesystem XML fragments installed with the
  bindings. `PySide6/glue/` and the top-level `qpy*.h/.cpp` helpers provide
  shared handwritten binding code.
- `plugins/uitools/` and `plugins/designer/` - Qt plugins that let Qt Designer
  and `pyside6-uic` discover Python widgets. They are optional and depend on
  the matching Qt development modules.
- `cmake/` - project setup, module-generation macros, and CMake package files.
  `tests/` and `doc/` contain binding tests and PySide documentation.

### `pyside-tools/` - Python command-line tools

Builds and installs the pure-Python `pyside6-*` commands, including deploy,
project, `qtpy2cpp`, `metaobjectdump`, and QML tooling. Qt's native tools such
as `uic`, `rcc`, `lupdate`, `qmlls`, Designer, Assistant, and Linguist come
from the Qt installation, not from this repository.

- `deploy.py`, `android_deploy.py`, and `ios_deploy.py` - entry points for
  `pyside6-deploy`, `pyside6-android-deploy`, and `pyside6-ios-deploy`.
- `deploy_lib/` - shared deployment implementation. `commands.py` executes
  external tools; `config.py` and `default.spec` load deployment settings;
  `dependency_util.py`, `deploy_util.py`, and `nuitka_helper.py` resolve
  dependencies, prepare packages, and run Nuitka; `pyproject_toml_deploy.py`
  and `python_helper.py` read project metadata and locate a Python runtime.
  - `deploy_lib/android/` - Android-specific configuration, dependency,
    packaging, and Buildozer helpers. Its `recipes/` templates initialise the
    PySide6 and shiboken6 packages in a python-for-android build.
  - `deploy_lib/ios/` - iOS-specific configuration, dependency, Info.plist,
    Xcode project, Objective-C++ entry-point, and Python XCFramework helpers.
  - The installed deployment library receives its canonical
    `android_utilities.py` and `python_xcframework.py` from
    `tools/cross_compile_android/` and `tools/cross_compile_ios/` respectively.
- `project.py` and `project_lib/` - implement `pyside6-project`: create,
  parse, maintain, and deploy `.pyproject` projects, including QRC generation
  and Qt Design Studio project support.
- `qtpy2cpp.py` and `qtpy2cpp_lib/` - convert selected Python/Qt code to C++.
  The library tokenises and visits Python syntax, builds an AST dump, formats
  generated code, and contains baseline tests.
- `metaobjectdump.py`, `qml.py`, and `pyside_tool.py` - introspection, QML,
  and common command dispatch helpers. `cmake/` contains the CMake setup and
  Android Java-bindings support used to package these tools.

## `tools/` - repository maintenance and build utilities

`tools/` is not installed in PySide wheels. It contains developer and release
utilities. The platform deployment tools above reuse the cross-compilation
helpers from this directory.

- `cross_compile_android/` and `cross_compile_ios/` - command-line drivers,
  dependency helpers, templates, and requirements for producing Android and
  iOS artifacts. The iOS directory also builds or obtains the Python
  XCFramework used by iOS deployment.
- `example_gallery/`, `sync_examples.py`, `regenerate_example_resources.py`,
  and `regenerate_example_ui.py` - generate, synchronise, and refresh example
  gallery content, resources, and generated UI files.
- `doc_modules.py`, `broken_links.py`, `scanqtclasses.py`,
  `missing_bindings/`, `snippets_translate/`, and `release_notes/` - build and
  check documentation inputs, compare Qt APIs with PySide coverage, translate
  C++ snippets to Python, and prepare release-note data.
- `checklibs.py`, `leak_finder.py`, `license_check.py`, and `uic_test.py` -
  platform library inspection, leak detection, licence checks, and `uic`
  validation.
- `dump_metaobject.py`, `metaobject_dump.py`, `qtcpp2py.py`,
  `debug_renamer.py`, and `debug_windows.py` - QMetaObject inspection,
  experimental C++/Python conversion, and debugging helpers.
- `create_changelog.py` and `install-p311.sh` - release and local
  environment-maintenance scripts.

## `build_scripts/` — Python build driver

- `main.py` — `PysideBuild` setuptools command (configure → build → install → package).
- `setup_runner.py` — runs `setup()` once per sub-project in dependency order.
- `options.py`, `config.py` — argparse flags (`--standalone`, `--limited-api`,
  `--internal-build-type`, `--skip-packaging`, etc.).
- `qtinfo.py` — `qmake -query` wrapper.
- `platforms/{linux,macos,unix,windows_desktop}.py` — `prepare_packages_*()`:
  copies from `install/` + bundles host Qt → `package/` and `package_for_wheels/`,
  fixes RPATHs, copies plugins/qml/translations.
- `wheel_files.py` — declares per-Qt-module file lists for the wheel split:
  `ModuleData` dataclass, `module_QtCore()/...`, `wheel_files_pyside_essentials()`,
  `wheel_files_pyside_addons()`. **The split between Essentials and Addons is
  defined here, not in CMake.**
- `wheel_utils.py`, `wheel_override.py` — custom `bdist_wheel` hooks.

## Generated `build/` trees

Out-of-source CMake roots. Inside `build/`, every Python venv used to build gets
its own subdirectory. **Naming convention** (postfix logic in
`create_wheels.get_build_directory()`):

- `build/<venv>` — plain release.
- `build/<venv>a` — limited API (abi3) release. *Most common; e.g. `.venva`.*
- `build/<venv>d` — debug.
- `build/<venv>da` — debug + limited API.

**Glob to find any build tree:** `build/.venv*` (regex: `build/\.venv[ad]*`).

Within each `build/<venv>/`:

```
build/<venv>/
├── build/              # CMake build trees — compilation happens here
├── install/            # CMake install prefix (DESTDIR-style, FHS layout)
├── package/            # flat single-wheel PySide6 layout (legacy staging)
└── package_for_wheels/ # split layout for create_wheels.py
```

### `build/<venv>/build/` — compilation

One subtree per sub-project: `shiboken6_generator/`, `shiboken6/`, `pyside6/`,
`pyside-tools/`.

**Where shiboken-generated wrappers live:**
`build/<venv>/build/pyside6/PySide6/Qt<Module>/PySide6/Qt<Module>/qXXX_wrapper.{cpp,h}`
— one pair per wrapped Qt class. Plus `pyside6_qt<module>_python.h` (umbrella),
`mjb_rejected_*.log` (per-module rejections), `mjb_shiboken.log`.

Compilation output: `Qt<Module>.abi3.so` (Linux), `.pyd` (Win), framework-dylib (macOS).

### `build/<venv>/install/` — CMake install prefix

Standard FHS-ish layout — what `cmake --install` produces. Both consumed by
the packaging step *and* usable as a system prefix:

```
install/
├── bin/                  # Qt host tools + Python tool wrappers
├── lib/                  # libshiboken6, libpyside6, libpyside6qml,
│   ├── cmake/            # PySide6Config / Shiboken6Config
│   ├── pkgconfig/        # .pc files
│   ├── python3.X/        # site-packages-style: PySide6/, shiboken6/
│   └── wheels/           # cmake configs marked for wheel installation
├── include/{PySide6,shiboken6}/
├── plugins/              # PySide6 designer/uic plugins
├── share/PySide6/        # typesystems, glue, doc glue
├── PySide6/              # importable: Qt<Module>.abi3.so + .pyi
├── shiboken6/            # importable Shiboken module
└── shiboken6_generator/  # shiboken6 binary + scripts
```

`generate_pyi.py` runs after the `.so` files land here and writes
`Qt<Module>.pyi` next to them.

### `build/<venv>/package/` — flat single-wheel staging

A single `PySide6/` directory laid out like the legacy monolithic wheel. Built
by `prepare_packages_*()`: copies from `install/` plus bundles required Qt libs,
plugins, qml, translations from the host Qt installation. Today this is just an
intermediate; `package_for_wheels/` is what actually feeds the wheels.

### `build/<venv>/package_for_wheels/` — split-wheel layout

Same content as `package/`, reorganized for the modern multi-wheel split:

```
package_for_wheels/
├── shiboken6/             # → shiboken6 wheel
├── shiboken6_generator/   # → shiboken6_generator wheel
└── PySide6/               # → split into PySide6_Essentials and PySide6_Addons
    ├── Qt<Module>.abi3.so + Qt<Module>.pyi   # all modules together here
    ├── PySide6_Essentials.json               # plugin manifests written by
    ├── PySide6_Addons.json                   # create_wheels.create_module_plugin_json()
    ├── Qt/                # bundled Qt: lib/ libexec/ plugins/ qml/
    │                      # translations/ metatypes/ modules/
    ├── lib/cmake/         # PySide6 CMake config (Essentials wheel only)
    ├── typesystems/, include/, glue/, doc/
    ├── scripts/, support/, QtAsyncio/
    ├── examples/          # only present when building the Examples wheel
    └── Assistant.app, Designer.app, Linguist.app   # macOS bundled apps
```

The Essentials/Addons classification is driven entirely by `wheel_files.py`.
`create_wheels.py` walks each module list, builds a `MANIFEST.in` against this
`PySide6/` directory, runs `python -m build` per wheel, and prunes leftovers
between wheels. The `Qt/` subtree is what makes wheels self-contained.

## End-to-end flow

1. `setup.py` → `SetupRunner` runs setuptools once per sub-project.
2. CMake configures each under `build/<venv>/build/<subproject>/`.
3. **shiboken6_generator** builds → produces the `shiboken6` executable.
4. **shiboken6** runtime builds.
5. **pyside6**: for each enabled Qt module, CMake invokes `shiboken6` with the
   typesystem XML + global header → emits `*_wrapper.cpp/.h` →
   compiled + linked against `libpyside6` + Qt → `Qt<Module>.abi3.so`.
6. **pyside-tools** install Python scripts.
7. `cmake --install` → everything to `build/<venv>/install/`.
8. `generate_pyi.py` introspects each `.so` → `Qt<Module>.pyi` next to it.
9. `prepare_packages_<platform>()` copies install/ + bundles Qt →
   `build/<venv>/package/` and `build/<venv>/package_for_wheels/`.
10. (Separately, on demand) `create_wheels.py` consumes `package_for_wheels/` +
    `wheel_files.py` + `wheel_artifacts/*.base` → `.whl` files in `dist/`.
