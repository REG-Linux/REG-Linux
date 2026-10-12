################################################################################
#
# hci-uart-rtk — Realtek Bluetooth HCI UART driver (replaces in-tree hci_uart)
#
################################################################################

HCI_UART_RTK_VERSION = 1.0
HCI_UART_RTK_SITE = $(HCI_UART_RTK_PKGDIR)/src
HCI_UART_RTK_SITE_METHOD = local
HCI_UART_RTK_LICENSE = GPL-2.0+

$(eval $(kernel-module))
$(eval $(generic-package))
