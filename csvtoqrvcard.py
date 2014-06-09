import qrcode
import csv

with open('/home/switlik/Documents/QR Badges/attendees.csv', 'rb') as csvfp:
    cvsfile = csv.reader(csvfp)
    for row in cvsfile:
        firstname = row[0]
        lastname = row[1]
        fullname = firstname+" "+lastname
        fullname = fullname.strip()
        institution = row[2]
        title_department = row[3]
        if title_department != "" and row[4] != "":
            title_department += ", "
        title_department += row[4]
        email = row[5]

        if fullname != "":
            #print fullname
            qrcontent = "BEGIN:VCARD\n"
            qrcontent += "VERSION:3.0\n"
            qrcontent += "N:"+fullname+"\n"
            if institution != "":
                qrcontent += "ORG:"+institution+"\n"
            if title_department != "":
                qrcontent += "TITLE:"+title_department+"\n"
            if email != "":
                qrcontent += "EMAIL:"+email+"\n"
            qrcontent += "END:VCARD\n"

            qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_L)
            qr.add_data(qrcontent)
            qr.make()
            im = qr.make_image()
            im.save("attendees/"+lastname+"_"+firstname+".png")
