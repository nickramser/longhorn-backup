FROM longhornio/longhorn-engine:v1.3.2

RUN zypper -n install tar python3-requests python3-six && rm -rf /var/cache/zypp/*

ADD longhorn.py /usr/local/bin
ADD longhorn-backup.py /usr/local/bin
ENTRYPOINT /usr/local/bin/longhorn-backup.py
