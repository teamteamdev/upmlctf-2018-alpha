# Deployment instructions

```bash
apt install -y python3 python3-pip
pip3 install --upgrade pip setuptools
rm /usr/bin/pip3
hash -r
pip3 install -r requirements.txt

mv notebook.service /etc/systemd/system/
systemctl daemon-reload

adduser --home /home/notebook --shell /usr/sbin/nologin --no-create-home --quiet notebook

chown -R root:notebook .
chmod -R o-rwx .

service notebook start

rm DEPLOYMENT.md
```
