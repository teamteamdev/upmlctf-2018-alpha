# Deployment instructions

```bash
apt install curl
curl -sL https://deb.nodesource.com/setup_8.x | bash -
apt install nodejs

mv hackergrom.service /etc/systemd/system/
systemctl daemon-reload

adduser --home /home/hackergrom --shell /usr/sbin/nologin --no-create-home --quiet hackergrom

sudo -u hackergrom npm -i

chown -R root:hackergrom .
chmod -R o-rwx .

service hackergrom start

rm DEPLOYMEMT.md
```

