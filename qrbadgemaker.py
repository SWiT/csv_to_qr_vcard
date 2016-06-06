import qrcode
import csv
import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4


drawtemplate    = False
schedule        = False
credit          = False
backside        = False
eventname       = ""
hashtag         = ""
csvfile         = ""
pdf             = ""

def displayHelp():
    print "Usage:"
    print "\tpython "+sys.argv[0]+" [OPTIONS] CSVFILE"
    print "Example:"
    print "\tpython "+sys.argv[0]+" --event \"Conference 2015\" --hashtag \"#Con2016\" attendees.csv"
    print "OPTIONS:"
    print "\t--template\t\tdraw the B-475 template lines"
    print "\t--credits\t\tdraw a back page with credit & URL."
    print "\t--schedule\t\tdraw a back page with a mini schedule."
    print "\t--event [\"NAME\"|IMAGE]\tSet the event name on the badge."
    print "\t--hashtag \"#HASHTAG\"\tSet the hashtag on the badge."
    print ""

def drawTemplateLines():
    # B-475 Template lines
    global inch, pdf
    pdf.setLineWidth(0.5)
    pdf.setDash([2,2], 0)
    pdf.line(0,0.125*inch, 8.5*inch,0.125*inch)
    pdf.line(0,5.4375*inch, 8.5*inch,5.4375*inch)
    pdf.line(0,10.625*inch, 8.5*inch,10.625*inch)
    pdf.line(4.25*inch,0.125*inch, 4.25*inch,10.625*inch)

def drawStringWrap(x,y, text, font, fontsize, maxwidth, lineheight, position = ""):
    textlines = [text]
    i = 0
    yoffset = 0
    pdf.setFont(font, fontsize)
    while i < len(textlines):
        textwidth = pdf.stringWidth(textlines[i], font, fontsize)
        if textwidth/(1*inch) < maxwidth:
            if position == "center":
                pdf.drawCentredString(x,y, textlines[i])
            elif position == "right":
                pdf.drawRightString(x,y, textlines[i])
            else:
                pdf.drawString(x,y, textlines[i])

            y = y - lineheight * inch
            i += 1
        else:
            splitpoint = int(len(textlines[i])/2)
            try:
                splitpoint = textlines[i][splitpoint:].index(" ") + splitpoint
            except ValueError:
                try:
                    splitpoint = textlines[i].index(" ")
                except ValueError:
                    print "ERROR: \""+textlines[i]+"\" is too long and can't be split."
                    quit()
            
            textlines.insert(i+1, textlines[i][splitpoint+1:])
            textlines[i] = textlines[i][:splitpoint]
            yoffset += lineheight * inch
        
    return yoffset

def drawBadge(pos):
    x = pos[0]
    y = pos[1]
    if backside:
        y -= 0.75*inch
        pdf.setFont("Helvetica", 11)

        # Draw the "made using blurb and url"
        if credit:
            pdf.drawCentredString(x,y, "This badge and QR code was made using")
            y -= 0.15*inch
            pdf.drawCentredString(x,y, "https://github.com/swit/qrbadgemaker")

        # Draw the mini schedule.
        if schedule:
            pdf.setLineWidth(0.5)
            pdf.setDash([1,1], 0)
            lineheight = 0.15
            fontsize = 10
            #open the schedulefile
            global csvfile
            schedulefp = open(csvfile, 'rb')
            scheduledata = csv.reader(schedulefp)
            for index,srow in enumerate(scheduledata):
                if len(srow) <= 0:
                    continue
                    
                if len(srow[0]) > 0 and srow[0][0] == '#':
                    continue

                starttime   = srow[0].strip()
                room1       = srow[1].strip()
                room2       = srow[2].strip()
                room3       = srow[3].strip()

                if index == 0:
                    fonttype = "Helvetica-Bold"    
                else:
                    fonttype = "Helvetica"            

                y -= lineheight * inch
                                
                yoffset = 0                                
                # Draw the Start time.
                yoffset = max(yoffset, drawStringWrap((x-1.65*inch),y, starttime, "Helvetica", fontsize, 0.4, lineheight, "right"))
                pdf.drawString(x,y, eventname)

                # Draw the titles of the presentations.
                if room2 == "" and room3 == "":
                    yoffset = max(yoffset, drawStringWrap((x-1.55*inch),y, room1, fonttype, fontsize, 3.5, lineheight))
                else:    
                    yoffset = max(yoffset, drawStringWrap((x-1.5*inch),y, room1, fonttype, fontsize, 1.0, lineheight))
                    yoffset = max(yoffset, drawStringWrap((x-0.3*inch),y, room2, fonttype, fontsize, 1.0, lineheight))
                    yoffset = max(yoffset, drawStringWrap((x+1.0*inch),y, room3, fonttype, fontsize, 1.0, lineheight))
                
                # Draw the vertical lines in this row
                if room1 != "":
                    pdf.line((x-1.6*inch), (y + lineheight * inch), (x-1.6*inch), (y-yoffset))
                if room2 != "":                
                    pdf.line((x-0.35*inch), (y + lineheight * inch), (x-0.35*inch), (y-yoffset)) 
                if room3 != "":
                    pdf.line((x+0.95*inch), (y + lineheight * inch), (x+0.95*inch), (y-yoffset))                

                y -= yoffset
    
                # Draw the horizontal line under this row.
                y -= 2
                pdf.line(0, y, 8.5*inch, y)
                
        #All day events
        y -= 2.25 * lineheight * inch
        drawStringWrap((x-2.0*inch),y, "The VR Experience: Sign up for sesssions in Room 125", fonttype, fontsize, 4.0, lineheight)
        y -= lineheight * inch
        drawStringWrap((x-2.0*inch),y, "8:30am - 4:15pm", fonttype, fontsize, 4.0, lineheight)
       
 
    else:
        # Draw the event name
        if eventnameusefile:
            y -= 1.05*inch
            pdf.drawImage(eventname, (x-1.8*inch),y, width=3.75*inch, height=0.43*inch, mask='auto')
        else:
            pdf.setFont("Helvetica-Bold", 27)
            y -= 0.8*inch
            pdf.drawCentredString(x,y, eventname)
        
        # Draw the attendees name
        pdf.setFont("Helvetica-Bold", 29)
        y -= 0.60*inch
        yoffset = drawStringWrap((x-0.05*inch),y, fullname, "Helvetica", 29, 4.0, 0.35, "center")
        y -= yoffset
        
        # Draw the attendees institution
        pdf.setFont("Helvetica", 23)
        y -= 0.35*inch
        yoffset = drawStringWrap(x,y, institution, "Helvetica", 23, 4.0, 0.35, "center")
        y -= yoffset
        
        # Draw the QR code
        y -= 2.325*inch
        pdf.drawInlineImage(imgfile, (x-1.1*inch),y, width=2.2*inch, height=2.2*inch)
        
        if (pos[1] - y)/inch > 5.4:
            print "ERROR: badge for \""+fullname+"\" contains too much information"
            quit()
        
        # Draw the hashtag
        pdf.setFont("Helvetica-Bold", 17)
        y = pos[1] - 5.4*inch
        pdf.drawCentredString(x,y, hashtag)
    return





#----------------------------
# Main Program Begins
#----------------------------

# Parse options and parameters.
for index, arg in enumerate(sys.argv):
    if arg == "--credit":
        backside = True
        credit = True

    elif arg == "--schedule":
        backside = True
        schedule = True

    elif arg == "--template":   
        drawtemplate = True

    elif arg == "--event":   
        eventname = sys.argv[index+1]

    elif arg == "--hashtag":   
        hashtag = sys.argv[index+1]

    elif os.path.splitext(arg)[1] == ".csv":
        csvfile = arg
     
# Validate options and parameters or display help.
error = False
if csvfile == "" and backside == False:
    error = True
elif csvfile != "" and not os.path.exists(csvfile):
    print
    print "ERROR: File '"+csvfile+"' not found."
    print
    error = True

if error:
    displayHelp()
    quit()


# Split off the filename for output.
filename = os.path.splitext(csvfile)[0]

# Check if eventname is an image file.
if os.path.exists(eventname):
    eventnameusefile = True
else:
    eventnameusefile = False

pdf = canvas.Canvas(filename+".pdf", pagesize=letter)
    
if backside:
    namesdata = [[".",".",".","."],[".",".",".","."],[".",".",".","."],[".",".",".","."]]
else:
    namesfp = open(csvfile, 'rb')
    namesdata = csv.reader(namesfp)

pagepos = 0
badgecount = 0

for row in namesdata:
    if len(row) <= 0:
        continue
        
    if row[0][0] == '#':
        continue

    firstname = row[0].strip()
    lastname = row[1].strip()
    fullname = firstname+" "+lastname
    institution = row[2].strip()
    email = row[3].strip()

    if drawtemplate:
        drawTemplateLines()

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
        
        # There seems to be a bug in reportlab.
        # Strings are drawn in the A4 template even though we've set the pagesize to letter.
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

os.remove(imgfile)

print        
print str(badgecount)+" Badges created in "+filename+".pdf"
print
    
