csv_to_qr_vcard
===============

A Python script to take a list of contacts in CSV format and generate QR codes in the vcard format.

INSTALLATION:

  sudo pip install pil qrcode

The CSV file should be called "attendees.csv" and be formatted with the following column order:

  First Name, Last Name, Institution, Title, Department, Email Address

RUN:

  python csvtoqrvcard.py
  
The QR code files are saved as "attendees/[Last Name_First Name].png"
