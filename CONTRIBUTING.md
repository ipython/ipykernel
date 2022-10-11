# Contributing

Welcome!

For contributing tips, follow the [Jupyter Contributing Guide](https://jupyter.readthedocs.io/en/latest/contributing/content-contributor.html).
Please make sure to follow the [Jupyter Code of Conduct](https://github.com/jupyter/governance/blob/master/conduct/code_of_conduct.md).

## Installing ipykernel for development

ipykernel is a pure Python package, so setting up for development is the same as most other Python projects:

```bash
# clone the repo
git clone https://github.com/ipython/ipykernel
cd ipykernel
# do a 'development' or 'editable' install with pip:
pip install -e .
```

## Code Styling

`ipykernel` has adopted automatic code formatting so you shouldn't
need to worry too much about your code style.
As long as your code is valid,
the pre-commit hook should take care of how it should look.
To install `pre-commit`, run the following::

```
pip install pre-commit
pre-commit install
```

You can invoke the pre-commit hook by hand at any time with::

```
pre-commit run
```

which should run any autoformatting on your code
and tell you about any errors it couldn't fix automatically.
You may also install [black integration](https://github.com/psf/black#editor-integration)
into your text editor to format code automatically.

If you have already committed files before setting up the pre-commit
hook with `pre-commit install`, you can fix everything up using
`pre-commit run --all-files`. You need to make the fixing commit
yourself after that.

Some of the hooks only run on CI by default, but you can invoke them by
running with the `--hook-stage manual` argument.

## Releasing ipykernel

Releasing ipykernel is _almost_ standard for a Python package:

- set version for release
- make and publish tag
- publish release to PyPI
- set version back to development

The one extra step for ipykernel is that we need to make separate wheels for Python 2 and 3
because the bundled kernelspec has different contents for Python 2 and 3. This
affects only the 4.x branch of ipykernel as the 5+ version is only compatible
Python 3.

The full release process is available below:

```bash
# make sure version is set in ipykernel/_version.py
VERSION="4.9.0"
# commit the version and make a release tag
git add ipykernel/_version.py
git commit -m "release $VERSION"
git tag -am "release $VERSION" $VERSION

# push the changes to the repo
git push
git push --tags

# publish the release to PyPI
# note the extra `python2 setup.py bdist_wheel` for creating
# the wheel for Python 2
pip install --upgrade twine
git clean -xfd
python3 setup.py sdist bdist_wheel
python2 setup.py bdist_wheel  # the extra step for the 4.x branch.
twine upload dist/*

# set the version back to '.dev' in ipykernel/_version.py
# e.g. 4.10.0.dev if we just released 4.9.0
git add ipykernel/_version.py
git commit -m "back to dev"
git push
```
