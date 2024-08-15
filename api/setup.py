# Copyright (c) 2020 Blank Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Usage:

bdist_wheel sdist
"""

import atexit
import os
import os.path as osp
import subprocess
import traceback
from pathlib import Path
from typing import List

import Cython
from Cython.Build import cythonize
from setuptools import Extension, setup

# ==============  version definition  ==============

PKG_NAME = "flowpilot"
PKG_VERSION = "0.1.0"
Cython.language_level = 3


def parse_version():
    return PKG_VERSION.replace("-", "")


def git_commit():
    try:
        cmd = ["git", "rev-parse", "HEAD"]
        git_commit = (
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
            )
            .communicate()[0]
            .strip()
        )
        git_commit = git_commit.decode()
    except:
        git_commit = "Unknown"

    return str(git_commit)


def write_version_py(filename="flowpilot/version.py"):
    ver_str = """# THIS FILE IS GENERATED FROM PADDLEPADDLE SETUP.PY
#
full_version    = '%(version)s'
commit          = '%(commit)s'
"""

    _git_commit = git_commit()
    with open(filename, "w") as f:
        f.write(ver_str % {"version": PKG_VERSION, "commit": _git_commit})


write_version_py()


def readme(fname):
    with open(fname, encoding="utf-8") as f:
        content = f.read()
    return content


def parse_requirements(fname):
    with open(fname, encoding="utf-8-sig") as f:
        requirements = f.readlines()
    return requirements


def delete_files(files: List[Path]):
    for f in files:
        try:
            f.unlink()
            print(f"removing {f}")
        except FileNotFoundError:
            print(f"FileNotFoundError {f}")
        except PermissionError:
            print(f"PermissionError {f}")
        except Exception as e:
            print(f"removing {f} Exception: {e}")


def split_cythonize_extensions(pkg_name: str, complie_files: List[str]):

    this_dir = Path(__file__).parent
    complie_files_fullpath = [this_dir / pkg_name / x for x in complie_files]

    extension_args = {
        "extra_compile_args": (
            ["/DWIN32", "/DWIN64"] if os.name == "nt" else ["-Os", "-g0"]
        ),
        "extra_link_args": ["/MACHINE:X64"] if os.name == "nt" else ["-Wl,--strip-all"],
    }

    keep_files, cythonize_files, extensions = [], [], []

    for filename in Path(this_dir / pkg_name).rglob("*.py"):
        if filename.name == "__init__.py" or filename not in complie_files_fullpath:
            keep_files.append(str(filename))
        else:
            cythonize_files.append(filename.with_suffix(".c"))
            module_path = filename.relative_to(this_dir).with_suffix("")
            module_name = ".".join(str(module_path).split(osp.sep))
            extensions.append(
                Extension(
                    module_name,
                    sources=[str(filename.relative_to(this_dir))],
                    **extension_args,
                )
            )

    atexit.register(delete_files, cythonize_files)

    ext_modules = cythonize(extensions, quiet=True, language_level=3)

    return keep_files, cythonize_files, ext_modules


if __name__ == "__main__":
    keep_files, cythonize_files, ext_modules = split_cythonize_extensions(
        "flowpilot", complie_files=[]
    )

    try:
        setup(
            name=PKG_NAME,
            packages=[""],
            package_data={"": keep_files + []},
            data_files=[
                # ('docker', [osp.abspath('docker/product/Dockerfile')]),
                # ('images', [osp.abspath(x) for x in glob.glob('images/*')])
            ],
            author="Blank",
            version=parse_version(),
            install_requires=parse_requirements("./requirements.txt"),
            description="flowpilot",
            long_description=readme("./README.md"),
            long_description_content_type="text/markdown",
            url="https://",
            download_url="",
            keywords=["flowpilot"],
            classifiers=[
                "Intended Audience :: Developers",
                "License :: OSI Approved :: Apache Software License",
                "Operating System :: OS Independent",
                "Natural Language :: Chinese (Simplified)",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                "Programming Language :: Python :: 3.12",
                "Topic :: Utilities",
            ],
            license="Apache License 2.0",
            # script_args=["build_ext", "-b", "build", "-t", "build/temp"],
            ext_modules=ext_modules,
            # cmdclass={'build_ext': build_ext},
            # cmdclass={
            #     'install_scripts': InstallScripts,
            # }
            entry_points={
                "console_scripts": [
                    # 'vinda=uvicorn vinda.api.app:app'
                ],
                # 'celery.commands': [
                #     'flower = flower.command.FlowerCommand',
                # ],
            },
        )
    except Exception as e:
        traceback.print_exc()
