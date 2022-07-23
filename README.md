# Longhorn-backup

Longhorn-backup is a utility which allows you to pull
[Longhorn](https://github.com/longhorn/longhorn) backups out of the longhorn
system into a tar file archive stored on any (usually non-longhorn) Kubernetes
volume. By default, longhorn stores all backups as blobs within the longhorn
system. These can be stored in NFS or S3, but the longhorn-engine is still
required to restore them. 

One of the major reasons I avoided migrating to longhorn for quite a while was
the lack of ability to truly backup my files in the simplest format, an
encrypted archive which can recovered without longhorn/docker/kubernetes in a
true DR scenario. This also protects against backup corruption by the
longhorn-engine itself. Last, the backups also serve to avoid lock-in to the
longhorn system if I want to move to another Kubernetes storage provider.

### How it works

Longhorn currently provides very [outdated
documentation](https://longhorn.io/docs/1.3.0/advanced-resources/data-recovery/recover-without-system/)
on how to restore backups to outside of the system (img or qcow2).  This
project is based on that functionality, but takes it much farther. It uses
the [Longhorn
API](https://longhorn.io/docs/1.3.0/references/longhorn-client-python/) to query
all of the volumes in the system and the configured backup target. It then
loops over all of the volumes, restores the latest backup to qcow2, mounts the
backup using nbd, and copies the files off into a `tgz` archive (optionally
encrypted). The archives are saved to `/backup/` within the container, which
can be any kubernetes supported volume. This allows your files to go straight to
another backup destination completely outside of Longhorn. 

### Prerequisites

 * Kubernetes worker nodes running longhorn-backup must have the `qemu-nbd`
   binary installed. On RHEL8, this is found in the `qemu-img` package. Systems
   must also have the `nbd` module inserted using modprobe. 
 * The container must run with `privileged: true` to allow access to
   `/dev/nbd*`.

### Caveats

* Currently only NFS backup target are tested/supported. Theoretically S3 should
  work by making sure the correct S3 env vars are setup, since the backup URL
  is pulled from the Longhorn API, see
  https://github.com/longhorn/longhorn/blob/v1.3.0/examples/restore_to_file.yaml.template.
  However, this has not be tested.

### Options

Currently there are two environment variables when can be used:
* `GPG` - Defaults to `False`. If set to true, backup archives will also be
  encrypted using `gpg` with a passphrase.
* `GPG_PASSPHRASE` - Must be set if `GPG` is `True`. The passphrase used to
  encrypt backups.

### Sample Kubernetes Usage

A sample kubernetes cronjob can be found in
[here](samples/longhorn-backup.cronjob.yml).

### Future Goals

This project is in an alpha state, and currently built for my specific needs.
As time permits, I plan to expand it by adding:
* Formal S3 support
* Include/Exclude filters for volumes
* Better error checking and logging (or really any error checking at all).
