service.conf
************

This file contains the specification of the services supported by the service, their measurement and action methods and their allowed actions.
Having this information hardcoded provides a safe way to operate on the machine services, especially when using systemd units instead of custom scripts.
This is because stuff from the client (presumably unsafe) is never directly written in a command.
Instead we write content from this list's items and its members.

.. _serviceconfsyntax:

Syntax
======
The file is a very simple config file, with a ``DEFAULT`` section and a unique section for each service. The key to each section acts as the ``id`` for that service.
The ``DEFAULT`` section in that file it propagated to all sections.

The following fields are recognized in every section:

* Name: the name of the service.
* Description: a description of what the service does.
* AllowedActions: a comma separated list of the actions that can be performed to the service. The only acceptable values here are: ``start, stop, restart, enable, disable`` and ``navigate``.
* MeasureMethod: one of the following (case insensitive keys):

    * ``systemd`` : status of the service should be measured by checking the status of a systemd unit, specified by ``MeasurementInstrument``.
    * ``systemd-user`` : status of the service should be measured by checking the status of a user systemd unit, specified by ``MeasurementInstrument``.
    * ``Script`` : the status of the service should be measured by running a custom script, which full path is specified in ``MeasurementInstrument``.

* MeasurementInstrument:

    * if ``MeasureMethod`` is either ``systemd`` or ``systemd-unit`` this must be a systemd unit (a user one in the case of ``systemd-unit``)
    * if ``MeasureMethod`` is ``Script`` this is the full path of the custom script. Said script when run should return a string in the form:

      .. code-block:: html

          <A> <E>

      where ``<A>`` can be: ``active, inactive, unknown``.
      and ``<E>`` can be: ``enabled, disabled, unknown``.

* ActionMethod: same as ``MeasureMethod``, but specify the way we will be operating on the service.
* MeasurementInstrument :

    * if ``MeasureMethod`` is either ``systemd`` or ``systemd-unit`` this must be a systemd unit (a user one in the case of ``systemd-unit``)
    * if ``MeasureMethod`` is ``Script`` this is the full path of the custom script. Said script should do the following:

                            * start the service when passed the arg ``start``
                            * stop the service when passed the arg ``stop``
                            * restart the service when passed the arg ``restart``
                            * enable the service when passed the arg ``enable`` (if applicable)
                            * disable the service when passed the arg ``disable`` (if applicable)

* NavigatePort: the destination port of the ``navigate`` action.

Example
=======

Below you can find an example of such specification:

.. code-block:: ini
  :linenos:

  [DEFAULT]
  AllowedActions=start,stop,restart,enable,disable,navigate

  [transmission]
  Name = Transmission Daemon
  Description = transmission-daemon is a daemon-based Transmission session that can be controlled via RPC commands from transmission's web interface or transmission-remote. The web interface runs on port 9091 of this server.
  MeasureMethod = systemd-user
  ActionMethod = systemd-user
  MeasurementInstrument = transmission.service
  ActionInstrument = transmission.service
  NavigatePort = 9091

  [kodi]
  Name = Kodi Mediacenter
  Description = Kodi is a free and open-source media player which allows users to play and view most streaming media, such as videos, music, podcasts, and videos from the internet, as well as all common digital media files from local and network storage media. Its web interface runs at port 8080 of this server.
  Unit = mediacenter.service
  MeasureMethod = systemd
  ActionMethod = Script
  MeasurementInstrument = mediacenter.service
  ActionInstrument = /home/osmc/kodi-manager-daemon/kodi-manager-daemon.sh
  NavigatePort = 8080

  [sickrage]
  Name = SiCKRAGE
  Description = Automatic Video Library Manager for TV Shows. It watches for new episodes of your favorite shows, and when they are posted it does its magic. Supports Torrent providers such as ThePirateBay, SceneAccess, TorrentDay, Rarbg, and many others.
  MeasureMethod = systemd-user
  ActionMethod = systemd-user
  MeasurementInstrument = sickrage.service
  ActionInstrument = sickrage.service
  NavigatePort = 8081
