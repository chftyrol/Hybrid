routing
*******

Synopsis
^^^^^^^^

This module provides the core functionality of the web service.

It defines the functionality of each web page, the relationships between them and it manages HTTP request, taking action upon them if necessary.

Members
^^^^^^^

.. automodule:: routing
   :members:
   :noindex:

Details of selected members
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _loginattempt:

Login Attempt
=============

The function accepts an HTTP ``POST`` request. The data of the request is available to the function through request.form.
request.form is a dictionary containing the data for the login request. It is like this:

.. code-block:: json

    {"attemptedid": "SHA256(attemptedpw)", "rememberme": "i"}

where ``i`` is an integer, taking values 0 (``== False``) and 1 (``== True``).

If the dictionary doesn't have either 1 or 2 key/value pairs, return a 400 Bad Request.
Otherwise read our ``loginDBFile``. Look for an entry with ``username`` == ``attemptedid``. If not found return a 401 Unauthorized.
Otherwise with bcrypt do a ``checkpw`` of ``SHA256(attemptedpw)`` against the stored password hash for the matching user.

If passwords don't match throw a 401 Unauthorized.
Otherwise, log in the user by setting ``session['logged_in'] = True``.
This will be checked by other functions when they need to see if the user is logged in.
If the user asked to be remembered bake a signed cookie with ``CookieBaker``.
We give it an expiration date and give it to the client.

.. _performaction:

Perform Action
==============

Look if the request for action corresponds (by ``Action`` and by ``Service``) to an allowed combination of ``Action`` and ``Service``
as specified by the list of :func:`helpers.get_services_list()`

If the request is for anything not allowed raise corresponding exceptions and return a 403 Forbidden error.
Otherwise the request is safe, so we take action.

The action taken depends on the ``actionMethod`` of the ``Service``.
In case of ``actionMethod == "systemd"`` run:

.. code-block:: sh

    $ systemctl <what> <who.unit>

Note that this approach is highly unrecommended because to be able to operate on global systemd units, the server must be run as root, which is a security hazard.
Instead prefer one of the following two approaches (with the first one being the safest).

In case of ``actionMethod == "systemd-user"`` run:

.. code-block:: sh

    $ systemctl --user <what> <who.unit>

In case of ``actionMethod == "script"`` run:

.. code-block:: sh

    $ <s.actionInstrument> <what>

where ``actionInstrument`` is a custom user script that has to accept the args ``start``, ``stop``, ``restart`` and if feasible ``enable`` and ``disable``
and act accordingly.

Manage the possible exceptions. If all is fine, return a 200 OK.

.. _measurestatus:

Measure Status
==============

The way the measurement is done is specified by ``measureMethod``: we use systemd units or custom user scripts.

In any case the output of the command must be of the form:

.. code-block:: html

    <A> <E>

where ``<A>`` can be: ``active``, ``inactive``, ``unknown``
and ``<E>`` can be: ``enabled``, ``disabled``, ``unknown``.

The results of the measurement are put in a JSON like:

.. code-block:: json

    {"status_all":{"kodi":"unavailable","sickrage":"unavailable","transmission":"inactive disabled"}}

and sent as a get response to the client.
