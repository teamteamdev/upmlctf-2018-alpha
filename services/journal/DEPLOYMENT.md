# Deployment instructions

```bash
apt install -y mono-complete socat
wget http://pascalabc.net/downloads/PABCNETC.zip
mkdir compiler
unzip PABCNETC.zip -d compiler
rm PABCNETC.zip

mv journal.service /etc/systemd/system/
systemctl daemon-reload

adduser --home /home/journal --shell /usr/sbin/nologin --no-create-home --quiet journal

service journal start

rm DEPLOYMENT.md
```

