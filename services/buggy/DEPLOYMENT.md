# Deployment instructions

```bash
apt install -y socat

mv buggy.service /etc/systemd/system/
systemctl daemon-reload

adduser --home /home/buggy --shell /usr/sbin/nologin --no-create-home --quiet buggy

mkdir storage
chown -R root:buggy .
chmod 770 storage
chmod 750 service

service buggy start

rm DEPLOYMENT.md
```

