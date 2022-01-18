# Overview

Fork from https://github.com/rohit0718/BBDC-Bot. Refer to upstream. 

## Background
The upstream code does not work for class 2b (bike) and had logic built to mass book for class 3 (car). Revisited the logic flow and did not integrate auto booking as it requires cancellation step. Moved from hassle of installing selenium to using selenium-chrome docker image. Using podman as I prefer it over docker :)  

## Changelog
### Added
- Added notification to telegram
### Updated
- Edited all code to be non deprecated 
- Edited logic flow as initial process does not match existing BBDC site
### Remove
- Original code was meant for mass booking of class 3 (car). Not well suited for class 2b (bike)
- Remove auto booking

# Prereqs
1. Install and setup environment
```
dnf upgrade -y
dnf install podman -y
podman run --privileged -d --network host --name chrome docker.io/selenium/standalone-chrome
cd /etc/systemd/user
podman generate systemd --new --files --name chrome
chmod 755 container-chrome.service
ln -s /etc/systemd/user/container-chrome.service /etc/systemd/system/container-chrome.service
systemctl daemon-reload
systemctl enable container-chrome.service
systemctl start container-chrome.service
```

2. Append variables to /etc/environment 
```
vi /etc/environment
chatid=
teleid=
BOOKING_PASSWORD=
BOOKING_USER=
```

3. Setup Cron and run script every 30min
```
dnf install cronie cronie-anacron -y 

sudo crontab -e
*/30 * * * * /usr/bin/python3 /root/BBDC-Bot/bbdc_bot.py >> ~/cron.log 2>&1
```
