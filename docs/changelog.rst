Changes in IPython kernel
=========================

4.5
---

4.5.2
*****

`4.5.2 on GitHub <https://github.com/ipython/ipykernel/milestones/4.5.2>`__

- Fix bug when instantating Comms outside of the IPython kernel (introduced in 4.5.1).


4.5.1
*****

`4.5.1 on GitHub <https://github.com/ipython/ipykernel/milestones/4.5.1>`__

- Add missing ``stream`` parameter to overridden :func:`getpass`
- Remove locks from iopub thread, which could cause deadlocks during debugging
- Fix regression where KeyboardInterrupt was treated as an aborted request, rather than an error
- Allow instantating Comms outside of the IPython kernel

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
- Remove refrences to outdated IPython guiref in kernel banner.
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
