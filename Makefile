all:
	:

test-hue:
	scp hue.py root@192.168.1.10:/var/lib/lxc/lxd/rootfs/var/lib/lxd/containers/iotctr/rootfs/var/lib/hue/app/hue.py
