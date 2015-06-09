import qrcode
import csv
import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

def displayHelp():
    print "Usage:"
    print "\tpython "+sys.argv[0]+" [OPTION] \"EVENTNAME\" \"HASHTAG\" CSVFILE"
    print "Example:"
    print "\tpython "+sys.argv[0]+" \"Conference 2015\" \"#Con2015\" attendees.csv"
    print "OPTIONS:"
    print "\t--drawtemplate\tdraw the B-475 template lines"
    print "\t--backcredits\tdraw a back page with credit & URL to QR Badge Maker."
    print "\t\t\tNo other parameters are required."
    print ""

   
if len(sys.argv) < 2 or len(sys.argv) > 5:
    displayHelp()
    quit()

drawtemplate = False
backcredits  = False

if sys.argv[1] == "--backcredits":
    backcredits = True
    eventname   = ""
    hashtag     = ""
    csvfile     = "back_credits.csv"
elif sys.argv[1] == "--drawtemplate":
    drawtemplate = True
    if len(sys.argv) == 5:
        eventname   = sys.argv[2]
        hashtag     = sys.argv[3]
        csvfile     = sys.argv[4]
    else:
        displayHelp()
        quit()
elif len(sys.argv) == 4:
    eventname   = sys.argv[1]
    hashtag     = sys.argv[2]
    csvfile     = sys.argv[3]
else:
    displayHelp()
    quit()

filename    = os.path.splitext(csvfile)[0]

#check if eventname is an image file
if os.path.exists(eventname):
    eventnameusefile = True
else:
    eventnameusefile = False

if backcredits:
    pdf = canvas.Canvas("back_credits.pdf", pagesize=letter)
else:
    pdf = canvas.Canvas(filename+".pdf", pagesize=letter)


def drawStringWrap(x,y, text, font, fontsize, maxwidth):
    textlines = [text]
    i = 0
    yoffset = 0
    while i < len(textlines):
        textwidth = pdf.stringWidth(textlines[i], font, fontsize)
        if textwidth/(1*inch) < maxwidth:
            pdf.drawCentredString(x,y, textlines[i])
            y = y - 0.35*inch
            i += 1
        else:
            splitpoint = int(len(textlines[i])/2)
            splitpoint = textlines[i][splitpoint:].index(" ") + splitpoint
            textlines.insert(i+1, textlines[i][splitpoint+1:])
            textlines[i] = textlines[i][:splitpoint]
            yoffset += 0.35*inch
        
    return yoffset

def drawBadge(pos, backcredits=False):
    if backcredits:
        # Draw the "made using blurb and url"
        pdf.setFont("Helvetica", 11)
        x = pos[0]
        y = pos[1] - 0.75*inch
        pdf.drawCentredString(x,y, "This badge and QR code was made using")
        y = pos[1] - 0.9*inch
        pdf.drawCentredString(x,y, "https://github.com/swit/qrbadgemaker")
        return
    
    # Draw the event name
    if eventnameusefile:
        x = pos[0] - 1.8*inch
        y = pos[1] - 1.05*inch
        pdf.drawImage(eventname, x,y, width=3.75*inch, height=0.43*inch, mask='auto')
    else:
        pdf.setFont("Helvetica-Bold", 27)
        x = pos[0]
        y = pos[1] - 0.8*inch
        pdf.drawCentredString(x,y, eventname)
    
    # Draw the attendees name
    pdf.setFont("Helvetica-Bold", 29)
    x = pos[0] - 0.05*inch
    y = pos[1] - 1.4*inch
    pdf.drawCentredString(x,y, fullname)
    
    # Draw the attendees institution
    pdf.setFont("Helvetica", 23)
    x = pos[0]
    y = pos[1] - 1.8*inch
    yoffset = drawStringWrap(x,y, institution, "Helvetica", 23, 4.0)
    
    # Draw the QR code
    x = pos[0] - 1.1*inch
    y = pos[1]- 4.125*inch - yoffset
    pdf.drawInlineImage(imgfile, x,y, width=2.2*inch, height=2.2*inch)
    
    # Draw the hashtag
    pdf.setFont("Helvetica-Bold", 17)
    x = pos[0]
    y = pos[1] - 5.45*inch
    pdf.drawCentredString(x,y, hashtag)
    
if backcredits:
    cvsfile = [[".",".",".","."],[".",".",".","."],[".",".",".","."],[".",".",".","."]]
elif not os.path.exists(csvfile):
    print
    print "ERROR: File '"+csvfile+"' not found."
    print
    displayHelp()
    quit()
else:
    csvfp = open(csvfile, 'rb')
    cvsfile = csv.reader(csvfp)

pagepos = 0
badgecount = 0

for row in cvsfile:
    if len(row) <= 0:
        continue
        
    if row[0][0] == '#':
        continue

    firstname = row[0].strip()
    lastname = row[1].strip()
    fullname = firstname+" "+lastname
    institution = row[2].strip()
    email = row[3].strip()

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
        imgfile = "temp.png"
        im.save(imgfile)
        
        if drawtemplate:
            # B-475 Template lines
            pdf.setLineWidth(0.5)
            pdf.setDash([2,2], 0)
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
        drawBadge(pos, backcredits)
            
        if pagepos >= 3:
            pdf.save()
            pagepos = -1
        
        pagepos += 1
        badgecount += 1
        
if pagepos != 0:
    pdf.save()

os.remove(imgfile)

print        
print str(badgecount)+" Badges created in "+filename+".pdf"
print
    
