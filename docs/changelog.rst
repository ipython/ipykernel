Changes in IPython kernel
=========================

4.2
---

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
