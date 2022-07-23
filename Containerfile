FROM longhornio/longhorn-engine:v1.3.0

# Needed due to https://github.com/longhorn/longhorn/issues/4191 until 1.3.1 
# is released containing upstream fix in longhorn-engine
RUN /bin/sed -i 's/SLE_15_SP3/15.3/g' /etc/zypp/repos.d/devel_tools_scm.repo

RUN zypper -n install tar python3-requests python3-six && rm -rf /var/cache/zypp/*

ADD longhorn.py /usr/local/bin
ADD longhorn-backup.py /usr/local/bin
ENTRYPOINT /usr/local/bin/longhorn-backup.py
