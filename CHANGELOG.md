# Changes in IPython kernel


## 6.0.0

IPykernel 6.0 is the first major release in about two years, that brings a number of improvements, code cleanup, and new
features to IPython.

You should be able to view all closed issues and merged Pull Request for this
milestone [on
GitHub](https://github.com/ipython/ipykernel/issues?q=milestone%3A6.0+is%3Aclosed+),
as for any major releases, we advise greater care when updating that for minor
release and welcome any feedback (~50 Pull-requests).

IPykernel 6 should contain all changes of the 5.x series, in addition to the
following non-exhaustive changes.


 - Support for the debugger protocol, when using `JupyterLab`, `RetroLab` or any
   frontend supporting the debugger protocol you should have access to the
   debugger functionalities.

 - The control channel on IPykernel 6.0 is run in a separate thread, this may
   change the order in which messages are processed, though this change was necessary
   to accommodate the debugger.

 - We now have a new dependency: `matplotlib-inline`, this helps to separate the
   circular dependency between IPython/IPykernel and  matplotlib.

 - All outputs to stdout/stderr should now be captured, including subprocesses
   and output of compiled libraries (blas, lapack....). In notebook
   server, some outputs that would previously go to the notebooks logs will now
   both head to notebook logs and in notebooks outputs. In terminal frontend
   like Jupyter Console, Emacs or other, this may ends up as duplicated outputs.

 - coroutines are now native (async-def) , instead of using tornado's
   `@gen.coroutine`

 - OutStreams can now be configured to report `istty() == True`, while this
   should make some output nicer (for example colored), it is likely to break
   others. Use with care.

## Deprecations in 6.0

 - `Kernel`s now support only a single shell stream, multiple streams will now be ignored. The attribute
   `Kernel.shell_streams` (plural) is deprecated in ipykernel 6.0. Use `Kernel.shell_stream` (singular)

 - `Kernel._parent_header` is deprecated, even though it was private. Use `.get_parent()` now.

## Removal in 6.0

 - `ipykernel.codeutils` was deprecated since 4.x series (2016) and has been removed, please import similar
   functionalities from `ipyparallel`

 - remove `find_connection_file` and `profile` argument of `connect_qtconsole` and `get_connection_info`, deprecated since IPykernel 4.2.2 (2016).


* Set `stop_on_error_timeout` default to 0.0 matching pre 5.5.0 default behavior with correctly working flag from 5.5.0.

## 5.5

### 5.5.5
* Keep preferring SelectorEventLoop on Windows. [#669](https://github.com/ipython/ipykernel/pull/669)

### 5.5.4
* Import ``configure_inline_support`` from ``matplotlib_inline`` if available [#654](https://github.com/ipython/ipykernel/pull/654)
   
### 5.5.3
* Revert Backport of #605: Fix Handling of ``shell.should_run_async`` [#622](https://github.com/ipython/ipykernel/pull/622)

### 5.5.2
**Note:** This release was deleted from PyPI since it had breaking changes.

* Changed default timeout to 0.0 seconds for stop_on_error_timeout. [#618](https://github.com/ipython/ipykernel/pull/618)

### 5.5.1
**Note:** This release was deleted from PyPI since it had breaking changes.

* Fix Handling of ``shell.should_run_async``. [#605](https://github.com/ipython/ipykernel/pull/605)

### 5.5.0
* kernelspec: ensure path is writable before writing `kernel.json`. [#593](https://github.com/ipython/ipykernel/pull/593)
* Add `configure_inline_support` and call it in the shell. [#590](https://github.com/ipython/ipykernel/pull/590)
* Fix `stop_on_error_timeout` to now properly abort `execute_request`'s that fall within the timeout after an error. [#572](https://github.com/ipython/ipykernel/pull/572)

## 5.4

### 5.4.3

* Rework `wait_for_ready` logic. [#578](https://github.com/ipython/ipykernel/pull/578)

### 5.4.2

* Revert \"Fix stop_on_error_timeout blocking other messages in
    queue\". [#570](https://github.com/ipython/ipykernel/pull/570)

### 5.4.1

* Invalid syntax in `ipykernel/log.py`. [#567](https://github.com/ipython/ipykernel/pull/567)

### 5.4.0

5.4.0 is generally focused on code quality improvements and tornado
asyncio compatibility.

* Add github actions, bail on asyncio patch for tornado 6.1.
    [#564](https://github.com/ipython/ipykernel/pull/564)
* Start testing on Python 3.9. [#551](https://github.com/ipython/ipykernel/pull/551)
* Fix stack levels for ipykernel\'s deprecation warnings and stop
    using some deprecated APIs. [#547](https://github.com/ipython/ipykernel/pull/547)
* Add env parameter to kernel installation [#541](https://github.com/ipython/ipykernel/pull/541)
* Fix stop_on_error_timeout blocking other messages in queue.
    [#539](https://github.com/ipython/ipykernel/pull/539)
* Remove most of the python 2 compat code. [#537](https://github.com/ipython/ipykernel/pull/537)
* Remove u-prefix from strings. [#538](https://github.com/ipython/ipykernel/pull/538)

## 5.3

### 5.3.4

* Only run Qt eventloop in the shell stream. [#531](https://github.com/ipython/ipykernel/pull/531)

### 5.3.3

* Fix QSocketNotifier in the Qt event loop not being disabled for the
    control channel. [#525](https://github.com/ipython/ipykernel/pull/525)

### 5.3.2

* Restore timer based event loop as a Windows-compatible fallback.
    [#523](https://github.com/ipython/ipykernel/pull/523)

### 5.3.1

* Fix \#520: run post_execute and post_run_cell on async cells
    [#521](https://github.com/ipython/ipykernel/pull/521)
* Fix exception causes in zmqshell.py [#516](https://github.com/ipython/ipykernel/pull/516)
* Make pdb on Windows interruptible [#490](https://github.com/ipython/ipykernel/pull/490)

### 5.3.0

5.3.0 Adds support for Trio event loops and has some bug fixes.

* Fix ipython display imports [#509](https://github.com/ipython/ipykernel/pull/509)
* Skip test_unc_paths if OS is not Windows [#507](https://github.com/ipython/ipykernel/pull/507)
* Allow interrupting input() on Windows, as part of effort to make pdb
    interruptible [#498](https://github.com/ipython/ipykernel/pull/498)
* Add Trio Loop [#479](https://github.com/ipython/ipykernel/pull/479)
* Flush from process even without newline [#478](https://github.com/ipython/ipykernel/pull/478)

## 5.2

### 5.2.1

* Handle system commands that use UNC paths on Windows
    [#500](https://github.com/ipython/ipykernel/pull/500)
* Add offset argument to seek in io test [#496](https://github.com/ipython/ipykernel/pull/496)

### 5.2.0

5.2.0 Includes several bugfixes and internal logic improvements.

* Produce better traceback when kernel is interrupted
    [#491](https://github.com/ipython/ipykernel/pull/491)
* Add `InProcessKernelClient.control_channel` for compatibility with
    jupyter-client v6.0.0 [#489](https://github.com/ipython/ipykernel/pull/489)
* Drop support for Python 3.4 [#483](https://github.com/ipython/ipykernel/pull/483)
* Work around issue related to Tornado with python3.8 on Windows
    ([#480](https://github.com/ipython/ipykernel/pull/480), [#481](https://github.com/ipython/ipykernel/pull/481))
* Prevent entering event loop if it is None [#464](https://github.com/ipython/ipykernel/pull/464)
* Use `shell.input_transformer_manager` when available
    [#411](https://github.com/ipython/ipykernel/pull/411)

## 5.1

### 5.1.4

5.1.4 Includes a few bugfixes, especially for compatibility with Python
3.8 on Windows.

* Fix pickle issues when using inline matplotlib backend
    [#476](https://github.com/ipython/ipykernel/pull/476)
* Fix an error during kernel shutdown [#463](https://github.com/ipython/ipykernel/pull/463)
* Fix compatibility issues with Python 3.8 ([#456](https://github.com/ipython/ipykernel/pull/456), [#461](https://github.com/ipython/ipykernel/pull/461))
* Remove some dead code ([#474](https://github.com/ipython/ipykernel/pull/474),
    [#467](https://github.com/ipython/ipykernel/pull/467))

### 5.1.3

5.1.3 Includes several bugfixes and internal logic improvements.

* Fix comm shutdown behavior by adding a `deleting` option to `close`
    which can be set to prevent registering new comm channels during
    shutdown ([#433](https://github.com/ipython/ipykernel/pull/433), [#435](https://github.com/ipython/ipykernel/pull/435))
* Fix `Heartbeat._bind_socket` to return on the first bind ([#431](https://github.com/ipython/ipykernel/pull/431))
* Moved `InProcessKernelClient.flush` to `DummySocket` ([#437](https://github.com/ipython/ipykernel/pull/437))
* Don\'t redirect stdout if nose machinery is not present ([#427](https://github.com/ipython/ipykernel/pull/427))
* Rename `_asyncio.py` to
    `_asyncio_utils.py` to avoid name conflicts on Python
    3.6+ ([#426](https://github.com/ipython/ipykernel/pull/426))
* Only generate kernelspec when installing or building wheel ([#425](https://github.com/ipython/ipykernel/pull/425))
* Fix priority ordering of control-channel messages in some cases
    [#443](https://github.com/ipython/ipykernel/pull/443)

### 5.1.2

5.1.2 fixes some socket-binding race conditions that caused testing
failures in nbconvert.

* Fix socket-binding race conditions ([#412](https://github.com/ipython/ipykernel/pull/412),
    [#419](https://github.com/ipython/ipykernel/pull/419))
* Add a no-op `flush` method to `DummySocket` and comply with stream
    API ([#405](https://github.com/ipython/ipykernel/pull/405))
* Update kernel version to indicate kernel v5.3 support ([#394](https://github.com/ipython/ipykernel/pull/394))
* Add testing for upcoming Python 3.8 and PEP 570 positional
    parameters ([#396](https://github.com/ipython/ipykernel/pull/396), [#408](https://github.com/ipython/ipykernel/pull/408))

### 5.1.1

5.1.1 fixes a bug that caused cells to get stuck in a busy state.

* Flush after sending replies [#390](https://github.com/ipython/ipykernel/pull/390)

### 5.1.0

5.1.0 fixes some important regressions in 5.0, especially on Windows.

[5.1.0 on GitHub](https://github.com/ipython/ipykernel/milestones/5.1)

* Fix message-ordering bug that could result in out-of-order
    executions, especially on Windows [#356](https://github.com/ipython/ipykernel/pull/356)
* Fix classifiers to indicate dropped Python 2 support
    [#354](https://github.com/ipython/ipykernel/pull/354)
* Remove some dead code [#355](https://github.com/ipython/ipykernel/pull/355)
* Support rich-media responses in `inspect_requests` (tooltips)
    [#361](https://github.com/ipython/ipykernel/pull/361)

## 5.0

### 5.0.0

[5.0.0 on GitHub](https://github.com/ipython/ipykernel/milestones/5.0)

* Drop support for Python 2. `ipykernel` 5.0 requires Python \>= 3.4
* Add support for IPython\'s asynchronous code execution
    [#323](https://github.com/ipython/ipykernel/pull/323)
* Update release process in `CONTRIBUTING.md` [#339](https://github.com/ipython/ipykernel/pull/339)

## 4.10

[4.10 on GitHub](https://github.com/ipython/ipykernel/milestones/4.10)

* Fix compatibility with IPython 7.0 [#348](https://github.com/ipython/ipykernel/pull/348)
* Fix compatibility in cases where sys.stdout can be None
    [#344](https://github.com/ipython/ipykernel/pull/344)

## 4.9

### 4.9.0

[4.9.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.9)

* Python 3.3 is no longer supported [#336](https://github.com/ipython/ipykernel/pull/336)
* Flush stdout/stderr in KernelApp before replacing
    [#314](https://github.com/ipython/ipykernel/pull/314)
* Allow preserving stdout and stderr in KernelApp
    [#315](https://github.com/ipython/ipykernel/pull/315)
* Override writable method on OutStream [#316](https://github.com/ipython/ipykernel/pull/316)
* Add metadata to help display matplotlib figures legibly
    [#336](https://github.com/ipython/ipykernel/pull/336)

## 4.8

### 4.8.2

[4.8.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.8.2)

* Fix compatibility issue with qt eventloop and pyzmq 17
    [#307](https://github.com/ipython/ipykernel/pull/307).

### 4.8.1

[4.8.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.8.1)

* set zmq.ROUTER_HANDOVER socket option when available to workaround
    libzmq reconnect bug [#300](https://github.com/ipython/ipykernel/pull/300).
* Fix sdists including absolute paths for kernelspec files, which
    prevented installation from sdist on Windows
    [#306](https://github.com/ipython/ipykernel/pull/306).

### 4.8.0

[4.8.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.8)

* Cleanly shutdown integrated event loops when shutting down the
    kernel. [#290](https://github.com/ipython/ipykernel/pull/290)
* `%gui qt` now uses Qt 5 by default rather than Qt 4, following a
    similar change in terminal IPython. [#293](https://github.com/ipython/ipykernel/pull/293)
* Fix event loop integration for `asyncio` when run with Tornado 5, which uses asyncio where
    available. [#296](https://github.com/ipython/ipykernel/pull/296)

## 4.7

### 4.7.0

[4.7.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.7)

* Add event loop integration for `asyncio`.
* Use the new IPython completer API.
* Add support for displaying GIF images (mimetype `image/gif`).
* Allow the kernel to be interrupted without killing the Qt console.
* Fix `is_complete` response with cell magics.
* Clean up encoding of bytes objects.
* Clean up help links to use `https` and improve display titles.
* Clean up ioloop handling in preparation for tornado 5.

## 4.6

### 4.6.1

[4.6.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.6.1)

* Fix eventloop-integration bug preventing Qt windows/widgets from
    displaying with ipykernel 4.6.0 and IPython ≥ 5.2.
* Avoid deprecation warnings about naive datetimes when working with
    jupyter_client ≥ 5.0.

### 4.6.0

[4.6.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.6)

* Add to API `DisplayPublisher.publish` two new fully
    backward-compatible keyword-args:

    > * `update: bool`
    > * `transient: dict`

* Support new `transient` key in
    `display_data` messages spec for `publish`.
    For a display data message, `transient` contains data
    that shouldn\'t be persisted to files or documents. Add a
    `display_id` to this `transient` dict by
    `display(obj, display_id=\...)`

* Add `ipykernel_launcher` module which removes the
    current working directory from `sys.path` before
    launching the kernel. This helps to reduce the cases where the
    kernel won\'t start because there\'s a `random.py` (or
    similar) module in the current working directory.

* Add busy/idle messages on IOPub during processing of aborted
    requests

* Add active event loop setting to GUI, which enables the correct
    response to IPython\'s `is_event_loop_running_xxx`

* Include IPython kernelspec in wheels to reduce reliance on \"native
    kernel spec\" in jupyter_client

* Modify `OutStream` to inherit from
    `TextIOBase` instead of object to improve API support
    and error reporting

* Fix IPython kernel death messages at start, such as \"Kernel
    Restarting\...\" and \"Kernel appears to have died\", when
    parent-poller handles PID 1

* Various bugfixes

## 4.5

### 4.5.2

[4.5.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.5.2)

* Fix bug when instantiating Comms outside of the IPython kernel
    (introduced in 4.5.1).

### 4.5.1

[4.5.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.5.1)

* Add missing `stream` parameter to overridden
    `getpass`
* Remove locks from iopub thread, which could cause deadlocks during
    debugging
* Fix regression where KeyboardInterrupt was treated as an aborted
    request, rather than an error
* Allow instantiating Comms outside of the IPython kernel

### 4.5.0

[4.5 on GitHub](https://github.com/ipython/ipykernel/milestones/4.5)

* Use figure.dpi instead of savefig.dpi to set DPI for inline figures
* Support ipympl matplotlib backend (requires IPython update as well
    to fully work)
* Various bugfixes, including fixes for output coming from threads,
    and `input` when called with
    non-string prompts, which stdlib allows.

## 4.4

### 4.4.1

[4.4.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.4.1)

* Fix circular import of matplotlib on Python 2 caused by the inline
    backend changes in 4.4.0.

### 4.4.0

[4.4.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.4)

* Use
    [MPLBACKEND](http://matplotlib.org/devel/coding_guide.html?highlight=mplbackend#developing-a-new-backend)
    environment variable to tell matplotlib \>= 1.5 use use the inline
    backend by default. This is only done if MPLBACKEND is not already
    set and no backend has been explicitly loaded, so setting
    `MPLBACKEND=Qt4Agg` or calling `%matplotlib notebook` or
    `matplotlib.use('Agg')` will take precedence.
* Fixes for logging problems caused by 4.3, where logging could go to
    the terminal instead of the notebook.
* Add `--sys-prefix` and `--profile` arguments to
    `ipython kernel install`.
* Allow Comm (Widget) messages to be sent from background threads.
* Select inline matplotlib backend by default if `%matplotlib` magic
    or `matplotlib.use()` are not called explicitly (for matplotlib \>=
    1.5).
* Fix some longstanding minor deviations from the message protocol
    (missing status: ok in a few replies, connect_reply format).
* Remove calls to NoOpContext from IPython, deprecated in 5.0.

## 4.3

### 4.3.2

* Use a nonempty dummy session key for inprocess kernels to avoid
    security warnings.

### 4.3.1

* Fix Windows Python 3.5 incompatibility caused by faulthandler patch
    in 4.3

### 4.3.0

[4.3.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.3)

* Publish all IO in a thread, via `IOPubThread`. This solves the problem of requiring
    `sys.stdout.flush` to be called in
    the notebook to produce output promptly during long-running cells.
* Remove references to outdated IPython guiref in kernel banner.
* Patch faulthandler to use `sys.__stderr__` instead of forwarded
    `sys.stderr`, which has no fileno when forwarded.
* Deprecate some vestiges of the Big Split:
    * `ipykernel.find_connection_file`
        is deprecated. Use
        `jupyter_client.find_connection_file` instead.

    \- Various pieces of code specific to IPython parallel are
    deprecated in ipykernel and moved to ipyparallel.

## 4.2

### 4.2.2

[4.2.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.2.2)

* Don\'t show interactive debugging info when kernel crashes
* Fix handling of numerical types in json_clean
* Testing fixes for output capturing

### 4.2.1

[4.2.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.2.1)

* Fix default display name back to \"Python X\" instead of \"pythonX\"

### 4.2.0

[4.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.2)

* Support sending a full message in initial opening of comms
    (metadata, buffers were not previously allowed)
* When using `ipython kernel install --name` to install the IPython
    kernelspec, default display-name to the same value as `--name`.

## 4.1

### 4.1.1

[4.1.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.1.1)

* Fix missing `ipykernel.__version__` on Python 2.
* Fix missing `target_name` when opening comms from the frontend.

### 4.1.0

[4.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.1)

* add `ipython kernel install` entrypoint for installing the IPython
    kernelspec
* provisional implementation of `comm_info` request/reply for msgspec
    v5.1

## 4.0

[4.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.0)

4.0 is the first release of ipykernel as a standalone package.
