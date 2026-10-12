# Synaptics DSX touchscreen driver (out-of-tree)
# From Android MSM kernel 4.19, stripped of Qualcomm dependencies

ccflags-y += -I$(src)

obj-m := synaptics_dsx_core.o synaptics_dsx_i2c.o

KVER ?= $(shell uname -r)
KDIR ?= /lib/modules/$(KVER)/build

all:
	mkdir -p $(KDIR)/include/linux/input
	cp -f $(PWD)/synaptics_dsx.h $(KDIR)/include/linux/input/
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
