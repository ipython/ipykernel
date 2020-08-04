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

import pytest

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
        'ipykernel_launcher',
        '-f',
        '{connection_file}'
    ])


def assert_kernel_dict(d):
    assert d['argv'] == make_ipkernel_cmd()
    assert d['display_name'] == 'Python %i' % sys.version_info[0]
    assert d['language'] == 'python'


def test_get_kernel_dict():
    d = get_kernel_dict()
    assert_kernel_dict(d)


def assert_kernel_dict_with_profile(d):
    nt.assert_equal(d['argv'], make_ipkernel_cmd(
        extra_arguments=["--profile", "test"]))
    assert d['display_name'] == 'Python %i' % sys.version_info[0]
    assert d['language'] == 'python'


def test_get_kernel_dict_with_profile():
    d = get_kernel_dict(["--profile", "test"])
    assert_kernel_dict_with_profile(d)


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
    assert path == path2
    assert_is_spec(path)
    shutil.rmtree(path)


@pytest.mark.skipif(sys.platform == 'win32',
                    reason="does not run on windows")
def test_write_kernel_spec_permissions():
    read_only_resources = os.path.join(tempfile.mkdtemp(), "_RESOURCES")
    shutil.copytree(RESOURCES, read_only_resources)

    # file used to check that the correct (mocked) resource directory was used
    with open(read_only_resources + '/touch', 'w') as f:
        pass

    # make copy of resources directory read-only
    os.chmod(read_only_resources, 0o500)
    for f in os.listdir(read_only_resources):
        os.chmod(os.path.join(read_only_resources, f), 0o400)

    with mock.patch('ipykernel.kernelspec.RESOURCES', read_only_resources):
        path = write_kernel_spec()

        assert_is_spec(path)

        # if `touch` is missing then the wrong resources directory was copied by
        # `write_kernel_spec`, `RESOURCES` mocking didn't work?
        assert os.path.isfile(path + '/touch')

        # ensure permissions are not loosened too much, original permission was
        # 0o500, so the 'fixed' one should be 0o700, still no rw for group/other
        assert os.stat(path).st_mode & 0o77 == 0o00

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


def test_install_profile():
    system_jupyter_dir = tempfile.mkdtemp()

    with mock.patch('jupyter_client.kernelspec.SYSTEM_JUPYTER_PATH',
            [system_jupyter_dir]):
        install(profile="Test")

    spec = os.path.join(system_jupyter_dir, 'kernels', KERNEL_NAME, "kernel.json")
    with open(spec) as f:
        spec = json.load(f)
    assert spec["display_name"].endswith(" [profile=Test]")
    nt.assert_equal(spec["argv"][-2:], ["--profile", "Test"])


def test_install_display_name_overrides_profile():
    system_jupyter_dir = tempfile.mkdtemp()

    with mock.patch('jupyter_client.kernelspec.SYSTEM_JUPYTER_PATH',
            [system_jupyter_dir]):
        install(display_name="Display", profile="Test")

    spec = os.path.join(system_jupyter_dir, 'kernels', KERNEL_NAME, "kernel.json")
    with open(spec) as f:
        spec = json.load(f)
    assert spec["display_name"] == "Display"
