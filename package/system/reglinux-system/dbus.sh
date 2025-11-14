#!/bin/dash
export DBUS_SESSION_BUS_ADDRESS="unix:path=/var/run/dbus/system_bus_socket"
[ -e /var/run/dbus ] || ln -s /run/dbus /var/run/dbus
