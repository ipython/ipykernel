Changes in IPython kernel
=========================

5.1
---

5.1.2
*****

5.1.2 fixes some socket-binding race conditions that caused testing failures in
nbconvert.

- Fix socket-binding race conditions (:ghpull: `412`, :ghpull: `419`)
- Add a no-op ``flush`` method to ``DummySocket`` and comply with stream API
  (:ghpull: `405`)
- Update kernel version to indicate kernel v5.3 support (:ghpull: `394`)
- Add testing for upcoming Python 3.8 and PEP 570 positional parameters
 (:ghpull: `396`, :ghpull: `408`)


5.1.1
*****
5.1.1 fixes a bug that caused cells to get stuck in a busy state.

- Flush after sending replies (:ghpull:`390`)


5.1.0
*****

5.1.0 fixes some important regressions in 5.0, especially on Windows.

`5.1.0 on GitHub <https://github.com/ipython/ipykernel/milestones/5.1>`__

- Fix message-ordering bug that could result in out-of-order executions,
  especially on Windows (:ghpull:`356`)
- Fix classifiers to indicate dropped Python 2 support (:ghpull:`354`)
- Remove some dead code (:ghpull:`355`)
- Support rich-media responses in ``inspect_requests`` (tooltips) (:ghpull:`361`)


5.0
---

5.0.0
*****

`5.0.0 on GitHub <https://github.com/ipython/ipykernel/milestones/5.0>`__

- Drop support for Python 2. ``ipykernel`` 5.0 requires Python >= 3.4
- Add support for IPython's asynchronous code execution (:ghpull:`323`)
- Update release process in ``CONTRIBUTING.md`` (:ghpull:`339`)


4.10
----

`4.10 on GitHub <https://github.com/ipython/ipykernel/milestones/4.10>`__

- Fix compatibility with IPython 7.0 (:ghpull:`348`)
- Fix compatibility in cases where sys.stdout can be None (:ghpull:`344`)

4.9
---

4.9.0
*****

`4.9.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.9>`__

- Python 3.3 is no longer supported (:ghpull:`336`)
- Flush stdout/stderr in KernelApp before replacing (:ghpull:`314`)
- Allow preserving stdout and stderr in KernelApp (:ghpull:`315`)
- Override writable method on OutStream (:ghpull:`316`)
- Add metadata to help display matplotlib figures legibly (:ghpull:`336`)


4.8
---

4.8.2
*****

`4.8.2 on GitHub <https://github.com/ipython/ipykernel/milestones/4.8.2>`__

- Fix compatibility issue with qt eventloop and pyzmq 17 (:ghpull:`307`).

4.8.1
*****

`4.8.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.8.1>`__

- set zmq.ROUTER_HANDOVER socket option when available
  to workaround libzmq reconnect bug (:ghpull:`300`).
- Fix sdists including absolute paths for kernelspec files,
  which prevented installation from sdist on Windows
  (:ghpull:`306`).

4.8.0
*****

`4.8.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.8>`__

- Cleanly shutdown integrated event loops when shutting down the kernel.
  (:ghpull:`290`)
- ``%gui qt`` now uses Qt 5 by default rather than Qt 4, following a similar
  change in terminal IPython. (:ghpull:`293`)
- Fix event loop integration for :mod:`asyncio` when run with Tornado 5,
  which uses asyncio where available. (:ghpull:`296`)

4.7
---

4.7.0
*****

`4.7.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.7>`__

- Add event loop integration for :mod:`asyncio`.
- Use the new IPython completer API.
- Add support for displaying GIF images (mimetype ``image/gif``).
- Allow the kernel to be interrupted without killing the Qt console.
- Fix ``is_complete`` response with cell magics.
- Clean up encoding of bytes objects.
- Clean up help links to use ``https`` and improve display titles.
- Clean up ioloop handling in preparation for tornado 5.


4.6
---

4.6.1
*****

`4.6.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.6.1>`__

- Fix eventloop-integration bug preventing Qt windows/widgets from displaying with ipykernel 4.6.0 and IPython ≥ 5.2.
- Avoid deprecation warnings about naive datetimes when working with jupyter_client ≥ 5.0.


4.6.0
*****

`4.6.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.6>`__

- Add to API `DisplayPublisher.publish` two new fully backward-compatible
  keyword-args:

    - `update: bool`
    - `transient: dict`

- Support new `transient` key in `display_data` messages spec for `publish`.
  For a display data message, `transient` contains data that shouldn't be
  persisted to files or documents. Add a `display_id` to this `transient`
  dict by `display(obj, display_id=...)`
- Add `ipykernel_launcher` module which removes the current working directory
  from `sys.path` before launching the kernel. This helps to reduce the cases
  where the kernel won't start because there's a `random.py` (or similar)
  module in the current working directory.
- Add busy/idle messages on IOPub during processing of aborted requests
- Add active event loop setting to GUI, which enables the correct response
  to IPython's `is_event_loop_running_xxx`
- Include IPython kernelspec in wheels to reduce reliance on "native kernel
  spec" in jupyter_client
- Modify `OutStream` to inherit from `TextIOBase` instead of object to improve
  API support and error reporting
- Fix IPython kernel death messages at start, such as "Kernel Restarting..."
  and "Kernel appears to have died", when parent-poller handles PID 1
- Various bugfixes


4.5
---

4.5.2
*****

`4.5.2 on GitHub <https://github.com/ipython/ipykernel/milestones/4.5.2>`__

- Fix bug when instantiating Comms outside of the IPython kernel (introduced in 4.5.1).


4.5.1
*****

`4.5.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.5.1>`__

- Add missing ``stream`` parameter to overridden :func:`getpass`
- Remove locks from iopub thread, which could cause deadlocks during debugging
- Fix regression where KeyboardInterrupt was treated as an aborted request, rather than an error
- Allow instantiating Comms outside of the IPython kernel

4.5.0
*****

`4.5 on GitHub <https://github.com/ipython/ipykernel/milestones/4.5>`__

- Use figure.dpi instead of savefig.dpi to set DPI for inline figures
- Support ipympl matplotlib backend (requires IPython update as well to fully work)
- Various bugfixes, including fixes for output coming from threads,
  and :func:`input` when called with non-string prompts, which stdlib allows.


4.4
---

4.4.1
*****

`4.4.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.4.1>`__

- Fix circular import of matplotlib on Python 2 caused by the inline backend changes in 4.4.0.


4.4.0
*****

`4.4.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.4>`__

- Use `MPLBACKEND`_ environment variable to tell matplotlib >= 1.5 use use the inline backend by default.
  This is only done if MPLBACKEND is not already set and no backend has been explicitly loaded,
  so setting ``MPLBACKEND=Qt4Agg`` or calling ``%matplotlib notebook`` or ``matplotlib.use('Agg')``
  will take precedence.
- Fixes for logging problems caused by 4.3,
  where logging could go to the terminal instead of the notebook.
- Add ``--sys-prefix`` and ``--profile`` arguments to :command:`ipython kernel install`
- Allow Comm (Widget) messages to be sent from background threads.
- Select inline matplotlib backend by default if ``%matplotlib`` magic or
  ``matplotlib.use()`` are not called explicitly (for matplotlib >= 1.5).
- Fix some longstanding minor deviations from the message protocol
  (missing status: ok in a few replies, connect_reply format).
- Remove calls to NoOpContext from IPython, deprecated in 5.0.

.. _MPLBACKEND: http://matplotlib.org/devel/coding_guide.html?highlight=mplbackend#developing-a-new-backend


4.3
---

4.3.2
*****

- Use a nonempty dummy session key for inprocess kernels to avoid security
  warnings.

4.3.1
*****

- Fix Windows Python 3.5 incompatibility caused by faulthandler patch in 4.3

4.3.0
*****

`4.3.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.3>`__

- Publish all IO in a thread, via :class:`IOPubThread`.
  This solves the problem of requiring :meth:`sys.stdout.flush` to be called in the notebook to produce output promptly during long-running cells.
- Remove references to outdated IPython guiref in kernel banner.
- Patch faulthandler to use ``sys.__stderr__`` instead of forwarded ``sys.stderr``,
  which has no fileno when forwarded.
- Deprecate some vestiges of the Big Split:
  - :func:`ipykernel.find_connection_file` is deprecated. Use :func:`jupyter_client.find_connection_file` instead.
  - Various pieces of code specific to IPython parallel are deprecated in ipykernel
  and moved to ipyparallel.


4.2
---

4.2.2
*****

`4.2.2 on GitHub <https://github.com/ipython/ipykernel/milestones/4.2.2>`__

- Don't show interactive debugging info when kernel crashes
- Fix handling of numerical types in json_clean
- Testing fixes for output capturing

4.2.1
*****

`4.2.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.2.1>`__

- Fix default display name back to "Python X" instead of "pythonX"

4.2.0
*****

`4.2 on GitHub <https://github.com/ipython/ipykernel/milestones/4.2>`_

- Support sending a full message in initial opening of comms (metadata, buffers were not previously allowed)
- When using ``ipython kernel install --name`` to install the IPython kernelspec, default display-name to the same value as ``--name``.

4.1
---

4.1.1
*****

`4.1.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.1.1>`_

- Fix missing ``ipykernel.__version__`` on Python 2.
- Fix missing ``target_name`` when opening comms from the frontend.

4.1.0
*****

`4.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.1>`_


-  add ``ipython kernel install`` entrypoint for installing the IPython
   kernelspec
-  provisional implementation of ``comm_info`` request/reply for msgspec
   v5.1

4.0
---

`4.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.0>`_

4.0 is the first release of ipykernel as a standalone package.
