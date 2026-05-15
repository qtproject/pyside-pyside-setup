Qt Network Authorization provides a set of APIs that enable Qt
applications to implement common authorization and authentication protocols.
For example, an application can implement access controls such as providing
limited access to online accounts and HTTP services without exposing user
passwords.

This module focuses on `OAuth 2.0`_ and provides limited support for
`OpenID`_. Refer to the section below about supported protocols.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtNetworkAuth


Supported Authorization and Authentication Protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Qt Network Authorization module supports functionalities from:

* `OAuth 1`_
* `OAuth 2.0`_
* `OpenID`_
* `OpenID Connect`_

These systems use a trusted **authorization server** for issuing access
tokens so that users do not send credentials to resources and resource
owners do not directly manage user credentials. For example, a user of a
cloud-based photo album website does not have to worry about passing their
credentials to the website. Instead, the credentials are
managed by a trusted authorization service through a web interface.

Articles and Guides
^^^^^^^^^^^^^^^^^^^

* :ref:`OAuth-2.0-Overview`
* :ref:`Qt-OAuth2-Browser-Support`
* :ref:`Qt-Network-Authorization-Security-Considerations`

.. _`OAuth`: https://oauth.net
.. _`OAuth 1`: https://oauth.net/1/
.. _`OAuth 2.0`: https://oauth.net/2/
.. _`OpenID`: http://openid.net/
.. _`OpenID Connect`: http://openid.net/connect/
