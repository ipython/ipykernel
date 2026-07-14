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
# do a 'development' or 'editable' install with pip,
# including the dependencies needed to run the test suite:
pip install -e ".[test]"
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

Releases are made with [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser);
see [RELEASE.md](RELEASE.md) for the process.
