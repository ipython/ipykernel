Changes in IPython kernel
=========================

4.3
---

4.3.0
*****

`4.3.0 on GitHub <https://github.com/ipython/ipykernel/milestones/4.3>`__

- Publish all IO in a thread, via :class:`IOPubThread`.
  This solves the problem of requiring :meth:`sys.stdout.flush` to be called in the notebook to produce output promptly during long-running cells.
- Remove refrences to outdated IPython guiref in kernel banner.
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
