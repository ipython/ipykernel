# Release Guide

## Using `jupyter_releaser`

The recommended way to make a release is to use [`jupyter_releaser`](https://github.com/jupyter-server/jupyter_releaser#checklist-for-adoption).

## Manual Release

- Update `CHANGELOG`

- Run the following:

```bash
export VERSION=<version>
pip install jupyter_releaser
tbump --only-patch $VERSION
git commit -a -m "Release $VERSION"
git tag $VERSION; true;
git push --all
git push --tags
rm -rf dist build
python -m build .
twine check dist/*
twine upload dist/*
```
