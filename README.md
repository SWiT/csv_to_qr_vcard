QR Badge Maker
===============

QR Badge Maker is a Python script that takes a list of conference attendees in a CSV file and generates B-475 Badges with QR codes in the vcard format.

###Setup
```
sudo pip install qrcode

wget https://github.com/SWiT/qrbadgemaker/archive/master.zip
unzip master.zip -d qrbadgemaker

OR

git clone https://github.com/SWiT/qrbadgemaker.git
```

###CSV File
The CSV file should be formatted with the following column order:
```
First Name, Last Name, Institution, Title, Department, Email Address
```
Note that Title and Department are not currently used.

###Run
```
python qrbadgemaker.py attendees.csv
```
The PDF of the badges will be called "attendees.pdf"
