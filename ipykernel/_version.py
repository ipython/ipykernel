"""
store the current version info of the server.
"""
import re

# Version string must appear intact for tbump versioning
__version__ = '6.9.1'

# Build up version_info tuple for backwards compatibility
pattern = r'(?P<major>\d+).(?P<minor>\d+).(?P<patch>\d+)(?P<rest>.*)'
match = re.match(pattern, __version__)
parts = [int(match[part]) for part in ['major', 'minor', 'patch']]
if match['rest']:
    parts.append(match['rest'])
version_info = tuple(parts)

kernel_protocol_version_info = (5, 3)
kernel_protocol_version = '%s.%s' % kernel_protocol_version_info
