QR Badge Maker
===============
Copyright (C) 2015 Matthew Gary Switlik

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

###About
QR Badge Maker is a Python script that takes a list of conference attendees in a CSV file and generates B-475 Badges with QR codes in the vcard format.

###Setup
```
sudo pip install qrcode

wget https://github.com/SWiT/qrbadgemaker/archive/master.zip
unzip master.zip -d qrbadgemaker
*OR*
git clone https://github.com/SWiT/qrbadgemaker.git
```

###CSV File
The CSV file should be formatted with the following column order:
```
First Name, Last Name, Institution, Email Address
```

###Run
```
python qrbadgemaker.py "Conference 2015" "#Con2015" attendees.csv
```
The PDF of the badges will be named whatever the CSV file was named with .pdf at the end.
