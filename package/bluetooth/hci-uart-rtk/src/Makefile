# Realtek Bluetooth HCI UART driver (out-of-tree)
# Replaces in-tree hci_uart — disable CONFIG_BT_HCIUART in kernel config

ccflags-y += -DCONFIG_BT_HCIUART_H4

obj-m := hci_uart_rtk.o
hci_uart_rtk-y := hci_ldisc.o hci_h4.o hci_rtk_h5.o rtk_coex.o

KVER ?= $(shell uname -r)
KDIR ?= /lib/modules/$(KVER)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

install:
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
