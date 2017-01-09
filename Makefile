all:
	:

test-hue:
	scp hue.py root@192.168.1.10:/var/lib/lxc/lxd/rootfs/var/lib/lxd/containers/iotctr/rootfs/var/lib/hue/app/hue.py
	scp templates/* root@192.168.1.10:/var/lib/lxc/lxd/rootfs/var/lib/lxd/containers/iotctr/rootfs/var/lib/hue/app/templates/
	scp autohome/* root@192.168.1.10:/var/lib/lxc/lxd/rootfs/var/lib/lxd/containers/iotctr/rootfs/var/lib/hue/app/autohome/
	scp static/* root@192.168.1.10:/var/lib/lxc/lxd/rootfs/var/lib/lxd/containers/iotctr/rootfs/var/lib/hue/app/static/
