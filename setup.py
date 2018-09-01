#!/usr/bin/env python
# coding: utf-8

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

# the name of the package
name = 'ipykernel'

#-----------------------------------------------------------------------------
# Minimal Python version sanity check
#-----------------------------------------------------------------------------

import sys

v = sys.version_info
if v[:2] < (2,7) or (v[0] >= 3 and v[:2] < (3,4)):
    error = "ERROR: %s requires Python version 2.7 or 3.4 or above." % name
    print(error, file=sys.stderr)
    sys.exit(1)

PY3 = (sys.version_info[0] >= 3)

#-----------------------------------------------------------------------------
# get on with it
#-----------------------------------------------------------------------------

from glob import glob
import os
import shutil

from setuptools import setup
from setuptools.command.bdist_egg import bdist_egg


class bdist_egg_disabled(bdist_egg):
    """Disabled version of bdist_egg

    Prevents setup.py install from performing setuptools' default easy_install,
    which it should never ever do.
    """
    def run(self):
        sys.exit("Aborting implicit building of eggs. Use `pip install .` to install from source.")


pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
pkg_root = pjoin(here, name)

packages = []
for d, _, _ in os.walk(pjoin(here, name)):
    if os.path.exists(pjoin(d, '__init__.py')):
        packages.append(d[len(here)+1:].replace(os.path.sep, '.'))

package_data = {
    'ipykernel': ['resources/*.*'],
}

version_ns = {}
with open(pjoin(here, name, '_version.py')) as f:
    exec(f.read(), {}, version_ns)


setup_args = dict(
    name=name,
    version=version_ns['__version__'],
    cmdclass={
        'bdist_egg': bdist_egg if 'bdist_egg' in sys.argv else bdist_egg_disabled,
    },
    scripts=glob(pjoin('scripts', '*')),
    packages=packages,
    py_modules=['ipykernel_launcher'],
    package_data=package_data,
    description="IPython Kernel for Jupyter",
    author='IPython Development Team',
    author_email='ipython-dev@scipy.org',
    url='https://ipython.org',
    license='BSD',
    platforms="Linux, Mac OS X, Windows",
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    setup_requires=['ipython', 'jupyter_core>=4.2'],
    install_requires=[
        'ipython>=4.0.0',
        'traitlets>=4.1.0',
        'jupyter_client',
        'tornado>=4.0',
    ],
    extras_require={
        'test:python_version=="2.7"': ['mock'],
        'test': [
            'pytest',
            'pytest-cov',
            'nose',  # nose because there are still a few nose.tools imports hanging around
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)

if any(a.startswith(('bdist', 'build', 'install')) for a in sys.argv):
    from ipykernel.kernelspec import write_kernel_spec, make_ipkernel_cmd, KERNEL_NAME

    argv = make_ipkernel_cmd(executable='python')
    dest = os.path.join(here, 'data_kernelspec')
    if os.path.exists(dest):
        shutil.rmtree(dest)
    write_kernel_spec(dest, overrides={'argv': argv})

    setup_args['data_files'] = [
        (
            pjoin('share', 'jupyter', 'kernels', KERNEL_NAME),
            glob(pjoin('data_kernelspec', '*')),
        )
    ]


if __name__ == '__main__':
    setup(**setup_args)
