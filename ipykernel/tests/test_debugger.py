from queue import Empty
import sys
import pytest

from .utils import TIMEOUT, new_kernel, get_reply

seq = 0

# Skip if debugpy is not available
pytest.importorskip("debugpy")


def wait_for_debug_request(kernel, command, arguments=None, full_reply=False):
    """Carry out a debug request and return the reply content.

    It does not check if the request was successful.
    """
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
    kernel.control_channel.send(msg)
    reply = get_reply(kernel, msg["header"]["msg_id"], channel="control")
    return reply if full_reply else reply["content"]


def wait_for_debug_event(kernel, event, timeout=TIMEOUT, verbose=False, full_reply=False):
    msg = {"msg_type": "", "content": {}}
    while msg.get('msg_type') != 'debug_event' or msg["content"].get("event") != event:
        msg = kernel.get_iopub_msg(timeout=timeout)
        if verbose:
            print(msg.get("msg_type"))
            if (msg.get("msg_type") == "debug_event"):
                print(f'  {msg["content"].get("event")}')
    return msg if full_reply else msg["content"]


def assert_stack_names(kernel, expected_names, thread_id=1):
    reply = wait_for_debug_request(kernel, "stackTrace", {"threadId": thread_id})
    names = [f.get("name") for f in reply["body"]["stackFrames"]]
    # "<module>" will be the name of the cell
    assert names == expected_names


@pytest.fixture
def kernel(request):
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    argv = getattr(request, "param", [])
    #argv.append("--log-level=DEBUG")
    with new_kernel(argv) as kc:
        yield kc


@pytest.fixture
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
        wait_for_debug_request(
            kernel, "disconnect", {"restart": False, "terminateDebuggee": True}
        )


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
    assert reply["success"]


def test_attach_debug(kernel_with_debug):
    reply = wait_for_debug_request(
        kernel_with_debug, "evaluate", {"expression": "'a' + 'b'", "context": "repl"}
    )
    assert reply["success"]
    assert reply["body"]["result"] == ""


def test_set_breakpoints(kernel_with_debug):
    code = """def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    source = r["body"]["sourcePath"]

    reply = wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 2}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )
    assert reply["success"]
    assert len(reply["body"]["breakpoints"]) == 1
    assert reply["body"]["breakpoints"][0]["verified"]
    assert reply["body"]["breakpoints"][0]["source"]["path"] == source

    r = wait_for_debug_request(kernel_with_debug, "debugInfo")
    assert source in map(lambda b: b["source"], r["body"]["breakpoints"])

    r = wait_for_debug_request(kernel_with_debug, "configurationDone")
    assert r["success"]


def test_stop_on_breakpoint(kernel_with_debug):
    code = """def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    source = r["body"]["sourcePath"]

    wait_for_debug_request(kernel_with_debug, "debugInfo")

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 2}, {"line": 5}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    wait_for_debug_request(kernel_with_debug, "configurationDone", full_reply=True)

    kernel_with_debug.execute(code)

    # Wait for stop on breakpoint
    msg = wait_for_debug_event(kernel_with_debug, "stopped")
    assert msg["body"]["reason"] == "breakpoint"
    stacks = wait_for_debug_request(
        kernel_with_debug,
        "stackTrace",
        {"threadId": r["body"].get("threadId", 1)}
    )["body"]["stackFrames"]
    names = [f.get("name") for f in stacks]
    assert stacks[0]["line"] == 5
    assert names == ["<module>"]

    wait_for_debug_request(kernel_with_debug, "continue", {"threadId": msg["body"].get("threadId", 1)})

    # Wait for stop on breakpoint
    msg = wait_for_debug_event(kernel_with_debug, "stopped")
    assert msg["body"]["reason"] == "breakpoint"
    stacks = wait_for_debug_request(
        kernel_with_debug,
        "stackTrace",
        {"threadId": r["body"].get("threadId", 1)}
    )["body"]["stackFrames"]
    names = [f.get("name") for f in stacks]
    assert names == ["f", "<module>"]
    assert stacks[0]["line"] == 2


def test_breakpoint_in_cell_with_leading_empty_lines(kernel_with_debug):
    code = """
def f(a, b):
    c = a + b
    return c

f(2, 3)"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    source = r["body"]["sourcePath"]

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

    # Wait for stop on breakpoint
    msg = wait_for_debug_event(kernel_with_debug, "stopped")
    assert msg["body"]["reason"] == "breakpoint"


def test_rich_inspect_not_at_breakpoint(kernel_with_debug):
    var_name = "text"
    value = "Hello the world"
    code = f"""{var_name}='{value}'
print({var_name})
"""

    msg_id = kernel_with_debug.execute(code)
    get_reply(kernel_with_debug, msg_id)

    r = wait_for_debug_request(kernel_with_debug, "inspectVariables")
    assert var_name in list(map(lambda v: v["name"], r["body"]["variables"]))

    reply = wait_for_debug_request(
        kernel_with_debug,
        "richInspectVariables",
        {"variableName": var_name},
    )

    assert reply["body"]["data"] == {"text/plain": f"'{value}'"}


@pytest.mark.parametrize("kernel", [["--Kernel.debug_just_my_code=False"]], indirect=True)
def test_step_into_lib(kernel_with_debug):
    code = """import traitlets
traitlets.validate('foo', 'bar')
"""

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    source = r["body"]["sourcePath"]

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 1}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    wait_for_debug_request(kernel_with_debug, "debugInfo")

    wait_for_debug_request(kernel_with_debug, "configurationDone")
    kernel_with_debug.execute(code)

    # Wait for stop on breakpoint
    r = wait_for_debug_event(kernel_with_debug, "stopped")
    assert r["body"]["reason"] == "breakpoint"
    assert_stack_names(kernel_with_debug, ["<module>"], r["body"].get("threadId", 1))

    # Step over the import statement
    wait_for_debug_request(kernel_with_debug, "next", {"threadId": r["body"].get("threadId", 1)})
    r = wait_for_debug_event(kernel_with_debug, "stopped")
    assert r["body"]["reason"] == "step"
    assert_stack_names(kernel_with_debug, ["<module>"], r["body"].get("threadId", 1))

    # Attempt to step into the function call
    wait_for_debug_request(kernel_with_debug, "stepIn", {"threadId": r["body"].get("threadId", 1)})
    r = wait_for_debug_event(kernel_with_debug, "stopped")
    assert r["body"]["reason"] == "step"
    assert_stack_names(kernel_with_debug, ["validate", "<module>"], r["body"].get("threadId", 1))


# Test with both lib code and only "my code"
@pytest.mark.parametrize("kernel", [[], ["--Kernel.debug_just_my_code=False"]], indirect=True)
def test_step_into_end(kernel_with_debug):
    code = 'a = 5 + 5\n'

    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    source = r["body"]["sourcePath"]

    wait_for_debug_request(
        kernel_with_debug,
        "setBreakpoints",
        {
            "breakpoints": [{"line": 1}],
            "source": {"path": source},
            "sourceModified": False,
        },
    )

    wait_for_debug_request(kernel_with_debug, "debugInfo")

    wait_for_debug_request(kernel_with_debug, "configurationDone")
    kernel_with_debug.execute(code)

    # Wait for stop on breakpoint
    r = wait_for_debug_event(kernel_with_debug, "stopped")

    # Attempt to step into the print statement (will continue execution, but
    # should stop on first line of next execute request)
    wait_for_debug_request(kernel_with_debug, "stepIn", {"threadId": r["body"].get("threadId", 1)})
    # assert no stop statement is given
    try:
        r = wait_for_debug_event(kernel_with_debug, "stopped", timeout=3)
    except Empty:
        pass
    else:
        # we're stopped somewhere. Fail with trace
        reply = wait_for_debug_request(kernel_with_debug, "stackTrace", {"threadId": r["body"].get("threadId", 1)})
        entries = []
        for f in reversed(reply["body"]["stackFrames"]):
            source = f.get("source", {}).get("path") or "<unknown>"
            loc = f'{source} ({f.get("line")},{f.get("column")})'
            entries.append(f'{loc}:  {f.get("name")}')
        raise AssertionError('Unexpectedly stopped. Debugger stack:\n    {0}'.format("\n    ".join(entries)))

    # execute some new code without breakpoints, assert it stops
    code = 'print("bar")\nprint("alice")\n'
    wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    kernel_with_debug.execute(code)
    wait_for_debug_event(kernel_with_debug, "stopped")


def test_rich_inspect_at_breakpoint(kernel_with_debug):
    code = """def f(a, b):
    c = a + b
    return c

f(2, 3)"""


    r = wait_for_debug_request(kernel_with_debug, "dumpCell", {"code": code})
    source = r["body"]["sourcePath"]

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

    # Wait for stop on breakpoint
    r = wait_for_debug_event(kernel_with_debug, "stopped")

    stacks = wait_for_debug_request(kernel_with_debug, "stackTrace", {"threadId": r["body"].get("threadId", 1)})[
        "body"
    ]["stackFrames"]

    scopes = wait_for_debug_request(
        kernel_with_debug, "scopes", {"frameId": stacks[0]["id"]}
    )["body"]["scopes"]

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
    if sys.platform == 'win32':
        from ipykernel.compiler import _convert_to_long_pathname
        _convert_to_long_pathname(__file__)
