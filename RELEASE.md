# Release Guide

- Update `docs/changelog.rst`
- Update `ipykernel/_version.py`
- Run the following:

```bash
version=`python setup.py --version 2>/dev/null`
git commit -a -m "Release $version"
git tag $version; true;
git push --all
git push --tags
rm -rf dist build
pip install build twine
python -m build .
pip install twine
twine check dist/* 
twine upload dist/*
```
