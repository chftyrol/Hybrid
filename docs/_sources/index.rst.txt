.. hybrid documentation master file, created by
   sphinx-quickstart on Wed May 24 01:13:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome | Hybrid's docs
=========================

Hybrid
^^^^^^
A simple web application to manage and access the services running on your home server.

Purpose
^^^^^^^^^^

I made this for my own personal use. Because the purpose it serves is somehow basic, it is not very interesting in itself.

What I think makes this useful is that it contains the barebone structure of a working website with some basic functionality.

For this reason Hybrid is very easy to adapt for projects that have nothing to do with its original scope.
Hence I encourage you to fork it and to make it your own.

Requirements
^^^^^^^^^^^^

This is a Python application and must be run under Python 3.
It depends on the following additional packages:

*  `bcrypt <https://pypi.python.org/pypi/bcrypt/>`_ 
*  `flask <http://flask.pocoo.org/>`_ 

It was tested only with ``bcrypt`` version 3.1.0 and ``flask`` version 0.12, which are the latest at the moment of release.

Installation
^^^^^^^^^^^^

There are two possibilities for the installation, depending on the use you plan to make of Hybrid.

As a barebone website
---------------------
If you don't care about Hybrid's original purpose, you can very well take the code and use it as a starting point for the website you have in mind.
This way you will have a simple way to display content, using the templating method, as well as a way to manage logins already worked out for you.

.. note::

  I made the decision not to include a page to create new users, because I should be the only user of the original website. If you plan to need a way to let new users register to your website, the python file ``userman.py`` will come in handy. It is a command line utility to manage users of the website. By taking (i.e. copy & pasting) functionality from it you should easily make yourself a 'Register' web page.

To install Hybrid run:

.. code-block:: sh

  $ git clone https://github.com/chftyrol/hybrid.git

on the machine you will run it from. Place the directory where you need it to be and start making it your own!

As a services manager
---------------------

Hybrid's original purpose is to manage other services on the same machine it runs on. Hence configuration is very subjective and varies user to user.

The installation of Hybrid is straightforward. Simply get yourself a copy of the application by cloning the repo:

.. code-block:: sh

  $ git clone --recursive https://github.com/chftyrol/hybrid.git

This adds to the barebone functionalities a directory containing installation and uninstallation scripts, as well as other files (shell scripts and systemd units mainly) that should give you an idea, together with the docs and the thoroughly commented installation scripts, of how I use Hybrid as a services manager.

**Configuration of the services manager**

An installation script is provided, which creates a dedicated user and group for Hybrid.
This script must be intended as a mere example, as it is the script I personally use and it is in no way general. In it there is an indication of the parts that can be customized to make it do what you want.

There is also a Makefile, which has a target called ``deploy``. Edit this to your needs if you are looking for a way to quickly deploy Hybrid to a remote server you have SSH access to.

The Hybrid Service Manager, the actual web service that lets you manage the services, is accessible through a login procedure.
To get some credentials you need to run the Python script provided with Hybrid, called ``userman.py``. It guides you step by step, so it should be easy to use.

A 'Register account' page is absent by choice.

If you want Hybrid  to actually manage something you will have to configure it to do so. This is done by editing the file ``services.conf`` to your needs.
For more info see :ref:`serviceconfsyntax`.

The one provided is just the configuration I use and it is an example. To make it work, the specifications in ``services.conf`` must be real.

e.g. If in ``services.conf`` you say you use a systemd user unit called ``boomer.service`` than it has to exist and be known to your system. The same holds with scripts.

The files in the directory ``install``, together with this docs should give you a clear idea of what configuring Hybrid means and how to do it properly.

Running
^^^^^^^

Simply run the Python script ``hybrid.py`` as an authorized user.

The default port on which the web service runs is 27172. To override this default behavior you can provide command line options.

You can learn all about them by running ``hybrid.py`` with the flag ``-h``.

Contributing
^^^^^^^^^^^^

There is surely much space to make Hybrid better. A couple of things come to mind right now:

* Make the mobile experience better, especially on the login page.
* Manage the issue with some browsers not displaying some unicode symbols (that are used as icons or for cosmetic reasons) properly.

If you are interested in this project I encourage you to contribute, in any way you want or can.

License
^^^^^^^

Hybrid is Free Software, released under the AGPL version 3 or later. When I say "Free" I mean free as in *free speech* not as in *free beer*. To learn more about this you can check out the `Free Software Foundation
<https://fsf.org>`_.

In this docs
^^^^^^^^^^^^
.. toctree::
   :maxdepth: 2

   cookiebaker
   helpers
   hybrid
   routing
   service

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
