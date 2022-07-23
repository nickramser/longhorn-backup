#!/usr/bin/env python3

import longhorn
import json
import os

# If automation/scripting tool is inside the same cluster in which Longhorn is installed
longhorn_url = 'http://longhorn-frontend.longhorn-system/v1'
# If forwarding `longhorn-frontend` service to localhost
#longhorn_url = 'http://localhost:8080/v1'

client = longhorn.Client(url=longhorn_url)
volumes = client.list_backupVolume().data
target = client.list_backupTarget().data
url = target[0].backupTargetURL

gpg_enable = os.getenv("GPG", 'False').lower() in ('true', '1')
if gpg_enable:
    gpg_passphrase = os.getenv('GPG_PASSPHRASE')

backups = []
for v in volumes:
    labels = json.loads(v.labels.KubernetesStatus)
    name = v.name
    label = labels['pvcName']
    backup = v.lastBackupName
    q_file = "/tmp/" + label + ".qcow2"
    if gpg_enable:
        t_file = "/backup/" + label + ".tgz.gpg"
    else:
        t_file = "/backup/" + label + ".tgz"
    os.system("longhorn backup restore-to-file '" + url + "?volume=" + name + "&backup=" + backup + "' --output-format qcow2 --output-file " + q_file)
    os.system("qemu-nbd --connect=/dev/nbd0 " + q_file)
    os.system("mount /dev/nbd0 /mnt")
    if gpg_enable:
        os.system("tar -czvf - -C /mnt . | gpg -c --batch --passphrase '" + gpg_passphrase + "' > " + t_file)
    else:
        os.system("tar -czvf " + t_file +  " -C /mnt .")
    os.system("umount /mnt")
    os.system("qemu-nbd --disconnect /dev/nbd0")


