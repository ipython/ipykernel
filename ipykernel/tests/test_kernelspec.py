# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import io
import os
import shutil
import sys
import tempfile
    
try:
    from unittest import mock
except ImportError:
    import mock # py2

from jupyter_core.paths import jupyter_data_dir

from ipykernel.kernelspec import (
    make_ipkernel_cmd,
    get_kernel_dict,
    write_kernel_spec,
    install,
    InstallIPythonKernelSpecApp,
    KERNEL_NAME,
    RESOURCES,
)

import nose.tools as nt

pjoin = os.path.join


def test_make_ipkernel_cmd():
    cmd = make_ipkernel_cmd()
    nt.assert_equal(cmd, [
        sys.executable,
        '-m',
        'ipykernel',
        '-f',
        '{connection_file}'
    ])


def assert_kernel_dict(d):
    nt.assert_equal(d['argv'], make_ipkernel_cmd())
    nt.assert_equal(d['display_name'], 'Python %i' % sys.version_info[0])
    nt.assert_equal(d['language'], 'python')


def test_get_kernel_dict():
    d = get_kernel_dict()
    assert_kernel_dict(d)


def assert_is_spec(path):
    for fname in os.listdir(RESOURCES):
        dst = pjoin(path, fname)
        assert os.path.exists(dst)
    kernel_json = pjoin(path, 'kernel.json')
    assert os.path.exists(kernel_json)
    with io.open(kernel_json, encoding='utf8') as f:
        json.load(f)


def test_write_kernel_spec():
    path = write_kernel_spec()
    assert_is_spec(path)
    shutil.rmtree(path)


def test_write_kernel_spec_path():
    path = os.path.join(tempfile.mkdtemp(), KERNEL_NAME)
    path2 = write_kernel_spec(path)
    nt.assert_equal(path, path2)
    assert_is_spec(path)
    shutil.rmtree(path)


def test_install_kernelspec():

    path = tempfile.mkdtemp()
    try: 
        test = InstallIPythonKernelSpecApp.launch_instance(argv=['--prefix', path])
        assert_is_spec(os.path.join(
            path, 'share', 'jupyter', 'kernels', KERNEL_NAME))
    finally:
        shutil.rmtree(path)


def test_install_user():
    tmp = tempfile.mkdtemp()
    
    with mock.patch.dict(os.environ, {'HOME': tmp}):
        install(user=True)
        data_dir = jupyter_data_dir()
    
    assert_is_spec(os.path.join(data_dir, 'kernels', KERNEL_NAME))


def test_install():
    system_jupyter_dir = tempfile.mkdtemp()
    
    with mock.patch('jupyter_client.kernelspec.SYSTEM_JUPYTER_PATH',
            [system_jupyter_dir]):
        install()
    
    assert_is_spec(os.path.join(system_jupyter_dir, 'kernels', KERNEL_NAME))


