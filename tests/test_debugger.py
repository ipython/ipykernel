import sys

import pytest

from .utils import TIMEOUT, get_replies, get_reply, new_kernel

seq = 0

# Tests support debugpy not being installed, in which case the tests don't do anything useful
# functionally as the debug message replies are usually empty dictionaries, but they confirm that
# ipykernel doesn't block, or segfault, or raise an exception.
try:
    import debugpy
except ImportError:
    debugpy = None


def prepare_debug_request(kernel, command, arguments=None):
    """Prepare a debug request but do not send it."""
    global seq
    seq += 1

    msg = kernel.session.msg(
        "debug_request",
        {
            "type": "request",
            "seq": seq,
            "command": command,
            "arguments": arguments or {},
        },
    )
    return msg


def wait_for_debug_request(kernel, command, arguments=None, full_reply=False):
    """Carry out a debug request and return the reply content.

    It does not check if the request was successful.
    """
    msg = prepare_debug_request(kernel, command, arguments)
    kernel.control_channel.send(msg)
    reply = get_reply(kernel, msg["header"]["msg_id"], channel="control")
    return reply if full_reply else reply["content"]


@pytest.fixture()
def kernel():
    with new_kernel() as kc:
        yield kc


@pytest.fixture()
def kernel_with_debug(kernel):
    # Initialize
    wait_for_debug_request(
        kernel,
        "initialize",
        {
            "clientID": "test-client",
            "clientName": "testClient",
            "adapterID": "",
            "pathFormat": "path",
            "linesStartAt1": True,
            "columnsStartAt1": True,
            "supportsVariableType": True,
            "supportsVariablePaging": True,
            "supportsRunInTerminalRequest": True,
            "locale": "en",
        },
    )

    # Attach
    wait_for_debug_request(kernel, "attach")

    try:
        yield kernel
    finally:
        # Detach
        wait_for_debug_request(kernel, "disconnect", {"restart": False, "terminateDebuggee": True})


def test_debug_initialize(kernel):
    reply = wait_for_debug_request(
        kernel,
        "initialize",
        {
            "clientID": "test-client",
            "clientName": "testClient",
            "adapterID": "",
            "pathFormat": "path",
            "linesStartAt1": True,
            "columnsStartAt1": True,
            "supportsVariableType": True,
            "supportsVariablePaging": True,
            "supportsRunInTerminalRequest": True,
            "locale": "en",
        },
    )
    if debugpy:
        assert reply["success"]
    else:
        assert reply == {}


def test_supported_features(kernel_with_debug):
    kernel_with_debug.kernel_info()
    reply = kernel_with_debug.get_shell_msg(timeout=TIMEOUT)
    supported_features = reply["content"]["supported_features"]

    if debugpy:
        assert "debugger" in supported_features
    else:
        assert "debugger" not in supported_features


def test_attach_debug(kernel_with_debug):
    reply = wait_for_debug_request(
        kernel_with_debug, "evaluate", {"expression": "'a' + 'b'", "context": "repl"}
    )
    if debugpy:
        assert reply["success"]
        assert reply["body"]["result"] == ""
    else:
        assert reply == {}


def test_set_breakpoints(kernel_with_debug):
    code = """def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    if debugpy:
        source = r["body"]["sourcePath"]
    else:
        assert r == {}
        source = "non-existent path"

    reply = wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 2}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )
    if debugpy:
        assert reply["success"]
        assert len(reply["body"]["breakpoints"]) == 1
        assert reply["body"]["breakpoints"][0]["verified"]
        assert reply["body"]["breakpoints"][0]["source"]["path"] == source
    else:
        assert reply == {}

    r = wait_for_debug_request(kernel_with_debug, "debugInfo")

    def func(b):
        return b["source"]

    if debugpy:
        assert source in map(func, r["body"]["breakpoints"])
    else:
        assert r == {}

    r = wait_for_debug_request(kernel_with_debug, "configurationDone")
    if debugpy:
        assert r["success"]
    else:
        assert r == {}


def test_stop_on_breakpoint(kernel_with_debug):
    code = """def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    if debugpy:
        source = r["body"]["sourcePath"]
    else:
        assert r == {}
        source = "some path"

    wait_for_debug_request(kernel_with_debug, "debugInfo")

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 2}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    wait_for_debug_request(kernel_with_debug, "configurationDone", full_reply=True)

    kernel_with_debug.execute(code)

    if not debugpy:
        # Cannot stop on breakpoint if debugpy not installed
        return

    # Wait for stop on breakpoint
    msg: dict = {"msg_type": "", "content": {}}
    while msg.get("msg_type") != "debug_event" or msg["content"].get("event") != "stopped":
        msg = kernel_with_debug.get_iopub_msg(timeout=TIMEOUT)

    assert msg["content"]["body"]["reason"] == "breakpoint"


def test_breakpoint_in_cell_with_leading_empty_lines(kernel_with_debug):
    code = """
def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    if debugpy:
        source = r["body"]["sourcePath"]
    else:
        assert r == {}
        source = "some path"

    wait_for_debug_request(kernel_with_debug, "debugInfo")

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 6}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    wait_for_debug_request(kernel_with_debug, "configurationDone", full_reply=True)

    kernel_with_debug.execute(code)

    if not debugpy:
        # Cannot stop on breakpoint if debugpy not installed
        return

    # Wait for stop on breakpoint
    msg: dict = {"msg_type": "", "content": {}}
    while msg.get("msg_type") != "debug_event" or msg["content"].get("event") != "stopped":
        msg = kernel_with_debug.get_iopub_msg(timeout=TIMEOUT)

    assert msg["content"]["body"]["reason"] == "breakpoint"


def test_rich_inspect_not_at_breakpoint(kernel_with_debug):
    var_name = "text"
    value = "Hello the world"
    code = f"""{var_name}='{value}'
print({var_name})
"""

    msg_id = kernel_with_debug.execute(code)
    get_reply(kernel_with_debug, msg_id)

    r = wait_for_debug_request(kernel_with_debug, "inspectVariables")

    def func(v):
        return v["name"]

    if debugpy:
        assert var_name in list(map(func, r["body"]["variables"]))
    else:
        assert r == {}

    reply = wait_for_debug_request(
        kernel_with_debug,
        "richInspectVariables",
        {"variableName": var_name},
    )

    if debugpy:
        assert reply["body"]["data"] == {"text/plain": f"'{value}'"}
    else:
        assert reply == {}


def test_rich_inspect_at_breakpoint(kernel_with_debug):
    code = """def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    if debugpy:
        source = r["body"]["sourcePath"]
    else:
        assert r == {}
        source = "some path"

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 2}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    r = wait_for_debug_request(kernel_with_debug, "debugInfo")

    r = wait_for_debug_request(kernel_with_debug, "configurationDone")

    kernel_with_debug.execute(code)

    if not debugpy:
        # Cannot stop on breakpoint if debugpy not installed
        return

    # Wait for stop on breakpoint
    msg: dict = {"msg_type": "", "content": {}}
    while msg.get("msg_type") != "debug_event" or msg["content"].get("event") != "stopped":
        msg = kernel_with_debug.get_iopub_msg(timeout=TIMEOUT)

    stacks = wait_for_debug_request(kernel_with_debug, "stackTrace", {"threadId": 1})["body"][
        "stackFrames"
    ]

    scopes = wait_for_debug_request(kernel_with_debug, "scopes", {"frameId": stacks[0]["id"]})[
        "body"
    ]["scopes"]

    locals_ = wait_for_debug_request(
        kernel_with_debug,
        "variables",
        {
            "variablesReference": next(filter(lambda s: s["name"] == "Locals", scopes))[
                "variablesReference"
            ]
        },
    )["body"]["variables"]

    reply = wait_for_debug_request(
        kernel_with_debug,
        "richInspectVariables",
        {"variableName": locals_[0]["name"], "frameId": stacks[0]["id"]},
    )

    assert reply["body"]["data"] == {"text/plain": locals_[0]["value"]}


def test_convert_to_long_pathname():
    if sys.platform == "win32":
        from ipykernel.compiler import _convert_to_long_pathname

        _convert_to_long_pathname(__file__)


def test_copy_to_globals(kernel_with_debug):
    local_var_name = "var"
    global_var_name = "var_copy"
    code = f"""from IPython.core.display import HTML
def my_test():
    {local_var_name} = HTML('<p>test content</p>')
    pass
a = 2
my_test()"""

    # Init debugger and set breakpoint
    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    if debugpy:
        source = r["body"]["sourcePath"]
    else:
        assert r == {}
        source = "some path"

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 4}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    wait_for_debug_request(kernel_with_debug, "debugInfo")

    wait_for_debug_request(kernel_with_debug, "configurationDone")

    # Execute code
    kernel_with_debug.execute(code)

    if not debugpy:
        # Cannot stop on breakpoint if debugpy not installed
        return

    # Wait for stop on breakpoint
    msg: dict = {"msg_type": "", "content": {}}
    while msg.get("msg_type") != "debug_event" or msg["content"].get("event") != "stopped":
        msg = kernel_with_debug.get_iopub_msg(timeout=TIMEOUT)

    stacks = wait_for_debug_request(kernel_with_debug, "stackTrace", {"threadId": 1})["body"][
        "stackFrames"
    ]

    # Get local frame id
    frame_id = stacks[0]["id"]

    # Copy the variable
    wait_for_debug_request(
        kernel_with_debug,
        "copyToGlobals",
        {
            "srcVariableName": local_var_name,
            "dstVariableName": global_var_name,
            "srcFrameId": frame_id,
        },
    )

    # Get the scopes
    scopes = wait_for_debug_request(kernel_with_debug, "scopes", {"frameId": frame_id})["body"][
        "scopes"
    ]

    # Get the local variable
    locals_ = wait_for_debug_request(
        kernel_with_debug,
        "variables",
        {
            "variablesReference": next(filter(lambda s: s["name"] == "Locals", scopes))[
                "variablesReference"
            ]
        },
    )["body"]["variables"]

    local_var = None
    for variable in locals_:
        if local_var_name in variable["evaluateName"]:
            local_var = variable
    assert local_var is not None

    # Get the global variable (copy of the local variable)
    globals_ = wait_for_debug_request(
        kernel_with_debug,
        "variables",
        {
            "variablesReference": next(filter(lambda s: s["name"] == "Globals", scopes))[
                "variablesReference"
            ]
        },
    )["body"]["variables"]

    global_var = None
    for variable in globals_:
        if global_var_name in variable["evaluateName"]:
            global_var = variable
    assert global_var is not None

    # Compare local and global variable
    assert global_var["value"] == local_var["value"] and global_var["type"] == local_var["type"]  # noqa: PT018


def test_debug_requests_sequential(kernel_with_debug):
    # Issue https://github.com/ipython/ipykernel/issues/1412
    # Control channel requests should be executed sequentially not concurrently.
    code = """def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    if debugpy:
        source = r["body"]["sourcePath"]
    else:
        assert r == {}
        source = "some path"

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 2}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    wait_for_debug_request(kernel_with_debug, "debugInfo")
    wait_for_debug_request(kernel_with_debug, "configurationDone")
    kernel_with_debug.execute(code)

    if not debugpy:
        # Cannot stop on breakpoint if debugpy not installed
        return

    # Wait for stop on breakpoint
    msg: dict = {"msg_type": "", "content": {}}
    while msg.get("msg_type") != "debug_event" or msg["content"].get("event") != "stopped":
        msg = kernel_with_debug.get_iopub_msg(timeout=TIMEOUT)

    stacks = wait_for_debug_request(kernel_with_debug, "stackTrace", {"threadId": 1})["body"][
        "stackFrames"
    ]

    scopes = wait_for_debug_request(kernel_with_debug, "scopes", {"frameId": stacks[0]["id"]})[
        "body"
    ]["scopes"]

    # Get variablesReference for both Locals and Globals.
    locals_ref = next(filter(lambda s: s["name"] == "Locals", scopes))["variablesReference"]
    globals_ref = next(filter(lambda s: s["name"] == "Globals", scopes))["variablesReference"]

    msgs = []
    for ref in [locals_ref, globals_ref]:
        msgs.append(
            prepare_debug_request(kernel_with_debug, "variables", {"variablesReference": ref})
        )

    # Send messages in quick succession.
    for msg in msgs:
        kernel_with_debug.control_channel.send(msg)

    replies = get_replies(kernel_with_debug, [msg["msg_id"] for msg in msgs], channel="control")

    # Check debug variable returns are correct.
    locals = replies[0]["content"]
    assert locals["success"]
    variables = locals["body"]["variables"]
    var = next(filter(lambda v: v["name"] == "a", variables))
    assert var["type"] == "int"
    assert var["value"] == "2"
    var = next(filter(lambda v: v["name"] == "b", variables))
    assert var["type"] == "int"
    assert var["value"] == "3"

    globals = replies[1]["content"]
    assert globals["success"]
    variables = globals["body"]["variables"]

    names = [v["name"] for v in variables]
    assert "function variables" in names
    assert "special variables" in names

    # Check status iopub messages alternate between busy and idle.
    execution_states = []
    while len(execution_states) < 8:
        msg = kernel_with_debug.get_iopub_msg(timeout=TIMEOUT)
        if msg["msg_type"] == "status":
            execution_states.append(msg["content"]["execution_state"])
    assert execution_states.count("busy") == 4
    assert execution_states.count("idle") == 4
    assert execution_states == ["busy", "idle"] * 4
