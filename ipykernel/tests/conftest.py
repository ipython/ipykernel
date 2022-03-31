import asyncio
import os

try:
    import resource
except ImportError:
    # Windows
    resource = None


# Handle resource limit
# Ensure a minimal soft limit of DEFAULT_SOFT if the current hard limit is at least that much.
if resource is not None:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)

    DEFAULT_SOFT = 4096
    if hard >= DEFAULT_SOFT:
        soft = DEFAULT_SOFT

    if hard < soft:
        hard = soft

    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))


# Enforce selector event loop on Windows.
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
