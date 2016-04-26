"""Import hooks to activate our inline backend when matplotlib is loaded
"""

import imp
import sys

def set_inline_backend(mpl):
    from IPython.core.pylabtools import backends, configure_inline_support
    from .kernelapp import IPKernelApp
    mpl.interactive(True)
    mpl.use(backends['inline'])
    configure_inline_support(IPKernelApp.instance().shell, backends['inline'])

class Py2MPLFinderShim(object):
    @classmethod
    def find_module(cls, fullname, path=None):
        if (fullname != 'matplotlib') or (path is not None):
            return None

        try:
            res = imp.find_module('matplotlib')
        except ImportError:
            return None
        else:
            return Py2MPLLoaderShim(*res)

class Py2MPLLoaderShim(object):
    def __init__(self, file, pathname, description):
        self.file = file
        self.pathname = pathname
        self.description = description

    def load_module(self, fullname):
        # fullname should only ever be 'matplotlib' here
        m = imp.load_module(fullname, self.file, self.pathname, self.description)
        set_inline_backend(m)
        return m

try:
    from importlib.machinery import PathFinder
except ImportError:
    # Python 2
    finder_shim = Py2MPLFinderShim
else:
    class Py3MPLFinderShim(PathFinder):
        # On Python 3.4 and above, find_spec() will be called
        @classmethod
        def find_spec(cls, fullname, path=None, target=None):
            if (fullname != 'matplotlib') or (path is not None):
                return None

            spec = PathFinder.find_spec(fullname, path=None)
            if spec is None:
                return None

            if spec.loader is not None:
                spec.loader = Py3MPLLoaderShim(spec.loader)
            return spec

        # On Python 3.3 or below, find_module() will be called
        @classmethod
        def find_module(cls, fullname, path=None):
            print(fullname, path)
            if (fullname != 'matplotlib') or (path is not None):
                return None

            real_loader = PathFinder.find_module(fullname, path=None)
            if real_loader is None:
                return None
            return Py3MPLLoaderShim(real_loader)

    class Py3MPLLoaderShim(object):
        def __init__(self, real_loader):
            self.real_loader = real_loader

        def load_module(self, fullname):
            # fullname should only ever be 'matplotlib' here)
            m = self.real_loader.load_module(fullname)
            set_inline_backend(m)
            return m


    finder_shim = Py3MPLFinderShim

def install_import_hook():
    sys.meta_path.insert(0, finder_shim)

def remove_import_hook():
    sys.meta_path.remove(finder_shim)
