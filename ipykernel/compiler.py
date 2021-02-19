from IPython.core.compilerop import CachingCompiler
import murmurhash.mrmr

def get_tmp_directory():
    return '/tmp/ipykernel_debugger/'

def get_tmp_hash_seed():
    hash_seed = 0xc70f6907
    return hash_seed

def get_file_name(code):
    name = murmurhash.mrmr.hash(code, seed = get_tmp_hash_seed(), murmur_version=2)
    if name < 0:
        name += 2**32
    return get_tmp_directory() + str(name) + '.py'

class XCachingCompiler(CachingCompiler):

    def __init__(self, *args, **kwargs):
        super(XCachingCompiler, self).__init__(*args, **kwargs)
        self.filename_mapper = None
        self.log = None

    def get_code_name(self, raw_code, code, number):
        filename = get_file_name(raw_code)

        if self.filename_mapper is not None:
            self.filename_mapper(filename, number)

        return filename

