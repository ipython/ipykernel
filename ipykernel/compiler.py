from IPython.core.compilerop import CachingCompiler
import tempfile
import os


def murmur2_x86(data, seed):
    m = 0x5bd1e995
    length = len(data)
    h = seed ^ length
    rounded_end = (length & 0xfffffffc)
    for i in range(0, rounded_end, 4):
        k = (ord(data[i]) & 0xff) | ((ord(data[i + 1]) & 0xff) << 8) | \
           ((ord(data[i + 2]) & 0xff) << 16) | (ord(data[i + 3]) << 24)
        k = (k * m) & 0xffffffff
        k ^= k >> 24
        k = (k * m) & 0xffffffff

        h = (h * m) & 0xffffffff
        h ^= k

    val = length & 0x03
    k = 0
    if val == 3:
        k = (ord(data[rounded_end + 2]) & 0xff) << 16
    if val in [2, 3]:
        k |= (ord(data[rounded_end + 1]) & 0xff) << 8
    if val in [1, 2, 3]:
        k |= ord(data[rounded_end]) & 0xff
        h ^= k
        h = (h * m) & 0xffffffff

    h ^= h >> 13
    h = (h * m) & 0xffffffff
    h ^= h >> 15

    return h


def get_tmp_directory():
    tmp_dir = tempfile.gettempdir()
    pid = os.getpid()
    return tmp_dir + '/ipykernel_' + str(pid)


def get_tmp_hash_seed():
    hash_seed = 0xc70f6907
    return hash_seed


def get_file_name(code):
    cell_name = os.environ.get("IPYKERNEL_CELL_NAME")
    if cell_name is None:
        name = murmur2_x86(code, get_tmp_hash_seed())
        cell_name = get_tmp_directory() + '/' + str(name) + '.py'
    return cell_name


class XCachingCompiler(CachingCompiler):

    def __init__(self, *args, **kwargs):
        super(XCachingCompiler, self).__init__(*args, **kwargs)
        self.log = None

    def get_code_name(self, raw_code, code, number):
        return get_file_name(raw_code)
