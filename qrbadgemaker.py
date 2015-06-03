import qrcode
import csv
import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

def displayHelp():
    print "Usage:"
    print "\tpython "+sys.argv[0]+" [OPTIONS] CSVFILE"
    print "OPTIONS:"
    print "\t--drawtemplate\tdraw the B-475 template lines"
    print ""
    
if len(sys.argv) < 2 or len(sys.argv) > 3:
    displayHelp()
    quit()

drawtemplate = False
if sys.argv[1] == "--drawtemplate":
    drawtemplate = True
    if len(sys.argv) == 3:
        csvfile     = sys.argv[2]
    else:
        displayHelp()
        quit()
else:
    csvfile     = sys.argv[1]
filename    = os.path.splitext(csvfile)[0]
directory   = filename

eventtitle  = "e-Cornucopia.2015"
hashtag     = "#ecorn15"

pdf = canvas.Canvas(filename+".pdf", pagesize=letter)

def drawBadge(pos):
    # Draw the event title
    pdf.setFont("Helvetica-Bold", 27)
    x = pos[0]
    y = pos[1] - 0.8*inch
    pdf.drawCentredString(x,y,eventtitle)
    
    # Draw the attendees name
    pdf.setFont("Helvetica-Bold", 29)
    x = pos[0]
    y = pos[1] - 1.4*inch
    pdf.drawCentredString(x,y,fullname)
    
    # Draw the attendees institution
    pdf.setFont("Helvetica", 23)
    x = pos[0]
    y = pos[1] - 1.8*inch
    pdf.drawCentredString(x,y,institution)
    
    # Draw the QR code
    x = pos[0] - 1.0*inch
    y = pos[1]- 3.9*inch
    pdf.drawImage(imgfile, x,y, width=2.0*inch, height=2.0*inch)
    
    # Draw the hashtag
    pdf.setFont("Helvetica-Bold", 17)
    x = pos[0]
    y = pos[1] - 5.5*inch
    pdf.drawCentredString(x,y,hashtag)
    
if not os.path.exists(csvfile):
    print "Error: File '"+csvfile+"' not found."
    displayHelp()
    quit()
    
with open(csvfile, 'rb') as csvfp:
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    pagepos = 0
    badgecount = 0
    cvsfile = csv.reader(csvfp)
    for row in cvsfile:
    	if len(row) <= 0:
    	    continue
    	if row[0][0] == '#':
    	    continue
    	firstname = row[0].strip()
        lastname = row[1].strip()
        fullname = firstname+" "+lastname
        fullname = fullname.strip()
        institution = row[2].strip()
        title_department = row[3].strip()
        if title_department != "" and row[4] != "":
            title_department += ", "
        title_department += row[4]
        email = row[5].strip()

        

        if fullname != "":
            qrcontent = "BEGIN:VCARD\n"
            qrcontent += "VERSION:3.0\n"
            qrcontent += "N:"+fullname+"\n"
            if institution != "":
                qrcontent += "ORG:"+institution+"\n"
            if email != "":
                qrcontent += "EMAIL:"+email+"\n"
            qrcontent += "END:VCARD\n"

            qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_L)
            qr.add_data(qrcontent)
            qr.make()
            im = qr.make_image()
            imgfile = directory+"/"+lastname+"_"+firstname+".png"
            im.save(imgfile)
            
            if drawtemplate:
                # B-475 Template lines
                pdf.line(0,0.125*inch, 8.5*inch,0.125*inch)
                pdf.line(0,5.4375*inch, 8.5*inch,5.4375*inch)
                pdf.line(0,10.625*inch, 8.5*inch,10.625*inch)
                pdf.line(4.25*inch,0.125*inch, 4.25*inch,10.625*inch)
            
            # There seems to be a bug in reportlab.
            # Strings are draw in the A4 template even though we've set the pagesize to letter.
            # Do text positioning based on A4.
            if pagepos == 0:
                pos = A4[0]/4, A4[1]-0.625*inch
            elif pagepos == 1:
                pos = A4[0]*3/4+0.25*inch, A4[1]-0.625*inch
            elif pagepos == 2:
                pos = A4[0]/4, A4[1]/2
            elif pagepos == 3:
                pos = A4[0]*3/4+0.25*inch, A4[1]/2
            drawBadge(pos)
                
            if pagepos >= 3:
                pdf.save()
                pagepos = -1
            
            pagepos += 1
            badgecount += 1
            
    if pagepos != 0:
        pdf.save()
            
    print str(badgecount)+" Badges created in "+filename+".pdf"
    
