#!/usr/bin/env python

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

# the name of the package
name = 'ipykernel'

#-----------------------------------------------------------------------------
# Minimal Python version sanity check
#-----------------------------------------------------------------------------

import sys
import re

v = sys.version_info
if v[:2] < (3, 5):
    error = "ERROR: %s requires Python version 3.5 or above." % name
    print(error, file=sys.stderr)
    sys.exit(1)

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

current_version = version_ns['__version__']

loose_pep440re = re.compile(r'^(\d+)\.(\d+)\.(\d+((a|b|rc)\d+)?)(\.post\d+)?(\.dev\d*)?$')
if not loose_pep440re.match(current_version):
    raise ValueError("Version number '%s' is not valid (should match [N!]N(.N)*[{a|b|rc}N][.postN][.devN])" % current_version)


setup_args = dict(
    name=name,
    version=current_version,
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
    long_description="The IPython kernel for Jupyter",
    platforms="Linux, Mac OS X, Windows",
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    python_requires='>=3.5',
    install_requires=[
        'ipython>=5.0.0',
        'traitlets>=4.1.0',
        'jupyter_client',
        'tornado>=4.2',
        'appnope;platform_system=="Darwin"',
    ],
    extras_require={
        'test': [
            'pytest !=5.3.4',
            'pytest-cov',
            'flaky',
            'nose',  # nose because there are still a few nose.tools imports hanging around
            'jedi<=0.17.2'
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)


if any(a.startswith(('bdist', 'install')) for a in sys.argv):
    from ipykernel.kernelspec import write_kernel_spec, make_ipkernel_cmd, KERNEL_NAME

    # When building a wheel, the executable specified in the kernelspec is simply 'python'.
    if any(a.startswith('bdist') for a in sys.argv):
        argv = make_ipkernel_cmd(executable='python')
    # When installing from source, the full `sys.executable` can be used.
    if any(a.startswith('install') for a in sys.argv):
        argv = make_ipkernel_cmd()
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
