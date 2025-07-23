#!/bin/bash

# Ensure the directory for the lock file exists and is owned by gvm.
# This part runs as root (the default user before gosu) to ensure permissions are set correctly.
mkdir -p /var/lib/openvas
chown gvm:gvm /var/lib/openvas
chmod 775 /var/lib/openvas # Give group write access as well, for broader compatibility

# Now execute the main command passed to the container as the gvm user.
exec gosu gvm "$@"
