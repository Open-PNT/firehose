#!/bin/bash

set -e

uid="$(ls -nd . | awk '{print $3}')"
gid="$(ls -nd . | awk '{print $4}')"

user="docker"
group="docker"

# Create an account
groupadd "$group" --non-unique -g "$gid"
useradd "$user" --non-unique -m -u "$uid" -g "$gid"
chown $user:$group /home/$user
echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

export HOME="/home/$user"

# If in CI, rewrite SSH URLs
if [[ -n $TOKEN_URL ]]; then
  echo -e \
  "[url \"$TOKEN_URL\"]\n\tinsteadOf = git@git.aspn.us:\n\tinsteadOf = ssh://git@git.aspn.us/" \
  > ~/.gitconfig
fi

# Run as account created above
exec runuser -g "$group" -u "$user" -- /bin/bash -c "$scl_args $@"
