pyVboxCmd
=========

License: LGPL/BSD.

Yet another Python library of Python bindings for Virtual Box CLI (Command Line Interface).

Motivation
--------

It appears that (VirtualBox)[https://www.virtualbox.org/] binary API is rather unstable, while CLI interface is quite stable. Plus, using CLI interface means that one has to compile bindings library for particular host being used. This can be not as simple as it should be on some systems (e.g. Windows). Binary bindings are also of a concern when packaging ones' program in to the redistributable packages.

To the best of my current knowledge, the only competing project worth noting is [pyvb](https://pypi.python.org/pypi/pyvb). But it seems to be rather dead at the moment with last release dating back to the 2008. And its GPL license is sadly not really suitable for my current needs.

Features
--------

The main difference of this library of bindings is that I am making "smart" objective bindings rather just set of Python functions that call corresponding CLI commands.

I am attempting to hide as much of low-level VM management as possible and to represent all VM--related entities (NICs, HDDs, etc. ) as Python objects with functions of their own and properties parsed to their corresponding Python objects.  Plus, I am attempting to make more consistent interface than VirtualBox'es CLI is.

Requirements
--------

Just a reasonably recent version of Python.

How do I use it?
--------

I will write this part eventually. Please refer to the code tests for now.

Can I contribute?
--------

Sure. That is why I am hosting on the GitHub. :-)