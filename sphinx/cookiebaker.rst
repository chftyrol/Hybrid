cookiebaker
************

Synopsis
^^^^^^^^

This module contains the implementation of the ``CookieBaker`` class.

``CookieBaker`` is a class implementing a manager of long-lived (as opposed to session-lived) login cookies.

Long-lived cookies
^^^^^^^^^^^^^^^^^^
Cookies consist of couples ::

  (cookieKey, cookieVal)

For our purpose cookieKey will always be ``rememberme``.

In this implementation, ``cookieVal`` is obtained as follows: 
  * Make a dictionary with the username as key and some random bytes from urandom as value.
  * Encode and sign this data using the JSON Web Signature (JWS) standard.

Members
^^^^^^^
.. automodule:: cookiebaker
   :noindex:

.. autoclass:: CookieBaker
   :members:
