# Release Guide

## Using `jupyter_releaser`

The recommended way to make a release is to use [`jupyter_releaser`](https://github.com/jupyter-server/jupyter_releaser#checklist-for-adoption).

## Manual Release

- Update `CHANGELOG`

- Run the following:

```bash
export VERSION=<version>
pip install pipx
pipx run hatch version $VERSION
git commit -a -m "Release $VERSION"
git tag $VERSION; true;
git push --all
git push --tags
rm -rf dist build
pipx run build .
pipx run twine check dist/*
pipx run twine upload dist/*
```
