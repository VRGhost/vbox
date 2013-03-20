VBox_
####################

License: BSD_.

Yet another Python library of Python_ bindings for Virtual Box CLI (Command Line Interface).

Motivation
********************

It appears that VirtualBox_ binary API is rather unstable, while CLI interface is quite
stable. Plus, using binary interface means that one has to compile bindings library for
particular host being used. This can be not as simple as it should be on some systems
(e.g. Windows). Binary bindings are also of a concern when packaging ones'
program in to the redistributable packages.

To the best of my current knowledge, the only competing project worth noting is pyvb_.
But it seems to be rather dead at the moment with last release dating back to the
2008. And its GPL license is sadly not really suitable for my current needs.

Features
********************

The main difference of this library of bindings is that I am making "smart" objective
bindings rather just set of Python functions that call corresponding CLI commands.

I am attempting to hide as much of low-level VM management as possible and to represent
all VM--related entities (NICs, HDDs, etc. ) as Python objects with functions of their own
and properties parsed to their corresponding Python objects.  Plus, I am attempting
to make more consistent interface than VirtualBox_'es CLI is.

Requirements
********************

Just a reasonably recent version of Python_.

How do I use it?
********************

Deployment
====================

You should be able to install this project via ``easy_install vbox`` route.

Alternatively, you can include this library as `git submodule`_. 
If you do that, please make sure to include this projects' ``release`` branch, not ``master``.
As ``release`` is the one that will contain versions of code that were actually released to the
`VBox pypy package page`_ , so you will get automatic code updates than,
but won't get all the frustration of me accidentally breaking something via
committing stuff to the ``master`` branch (that is development/testing branch).

API
====================

I will write this part eventually. Please refer to the `VBox tests`_ for now.

Creating VM
********************

VM with no drives and default amounts of RAM for the selected OS type is created
with the following command:

::

    import vbox

    vm = vbox.VM(
        vbox.General(
            name="foo",
            osType="Windows95",
        ),
        vbox.Storage(),
    )


VM with 10gb HDD and an empty DVD drive
^^^^^^^^^^^^^^^^^^^^



Contributions
********************

Please do feel free to email me your suggestions on how to improve this library. Just email me (address can be found in the ``setup.py`` file or just googled for).

Can I has code?
====================

Sure. That is why I am hosting VBox_ on the GitHub. :-)

.. _BSD: http://opensource.org/licenses/BSD-3-Clause
.. _Python: http://www.python.org/
.. _pyvb: https://pypi.python.org/pypi/pyvb
.. _VBox tests: https://github.com/VRGhost/vbox/tree/master/src/tests
.. _VBox: https://github.com/VRGhost/vbox
.. _VirtualBox: https://www.virtualbox.org/
.. _git submodule: http://git-scm.com/book/en/Git-Tools-Submodules
.. _VBox pypy package page: https://pypi.python.org/pypi/vbox