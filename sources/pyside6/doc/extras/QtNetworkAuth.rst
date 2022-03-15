Provides network authorization capabilities (OAuth).

Qt Network Authorization provides a set of APIs that enable Qt applications to
obtain limited access to online accounts and HTTP services without exposing
users' passwords.

Currently, the supported authorization protocol is `OAuth <https://oauth.net>`_
, versions 1 and 2.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtNetworkAuth

Overview
^^^^^^^^

The goal of this module is to provide a way to handle different authentication
methods present on the Internet.

There are several authentication systems, including:

    * `OAuth 1 <https://datatracker.ietf.org/doc/html/rfc5849>`_
    * `OAuth 2 <https://datatracker.ietf.org/doc/html/rfc6749>`_
    * `OpenID <http://openid.net>`_
    * `OpenID Connect <http://openid.net/connect/>`_

These systems allow the application developers to create applications which use
external authentication servers provided by an *Authorization Server*\. Users
of these services need not worry about passing their credentials to suspicious
applications. Instead, the credentials are entered in a known and trusted web
interface.
