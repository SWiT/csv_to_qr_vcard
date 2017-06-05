import qrcode
import csv
import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

class qrbadgemaker:
    def __init__(self):
        self.drawtemplate   = False
        self.schedule       = False
        self.eventname      = ""
        self.hashtag        = ""
        self.csvfile        = ""
        self.pdf            = ""
        self.badgeformat    = "B475"
        self.badgesperpage  = 4


    def displayHelp(self):
        print "Usage:"
        print "\tpython "+sys.argv[0]+" [OPTIONS] CSVFILE"
        print "Example:"
        print "\tpython "+sys.argv[0]+" --event \"Conference 2015\" --hashtag \"#Con2016\" attendees.csv"
        print "OPTIONS:"
        print "\t--template\t\tDraw the template lines"
        print "\t--format [B475|B628]\tBadge format to use [Default:B475]"
        print "\t--schedule\t\tDraw a back page with a mini schedule."
        print "\t--event [\"NAME\"|IMAGE]\tSet the event name on the badge."
        print "\t--hashtag \"#HASHTAG\"\tSet the hashtag on the badge."
        print ""

    def newpage(self):
        self.pdf.save()
        self.pdf.translate((-3.0/16*inch), (-9.0/32*inch))
        return

    def drawTemplateLines(self):
        global inch
        self.pdf.setLineWidth(0.5)
        self.pdf.setDash([2,2], 0)
        self.pdf.setStrokeColorRGB(0.85,0.85,0.85)
        if self.badgeformat == "B475":
            # B-475 Template lines
            self.pdf.line(0,0.125*inch, 8.5*inch,0.125*inch)             # bottom margin
            self.pdf.line(0,5.4375*inch, 8.5*inch,5.4375*inch)           # horizontal middle divide
            self.pdf.line(0,10.625*inch, 8.5*inch,10.625*inch)           # top margin
            self.pdf.line(4.25*inch,0.125*inch, 4.25*inch,10.625*inch)   # vertical middle divide
        elif self.badgeformat == "B628":
            # B-628 Template lines
            self.pdf.line(0*inch, 10.5*inch, 8.5*inch, 10.5*inch)           # top margin
            self.pdf.line(0*inch, 8.5*inch, 8.5*inch, 8.5*inch)             # ticket 1
            self.pdf.line(0*inch, 6.5*inch, 8.5*inch, 6.5*inch)             # ticket 2
            self.pdf.line(0*inch, 0.5*inch, 8.5*inch, 0.5*inch)         # bottom margin

            self.pdf.line(0.25*inch, 0*inch, 0.25*inch, 10.5*inch)     # left margin
            self.pdf.line(4.25*inch, 0*inch, 4.25*inch, 10.5*inch)   # vertical middle divide
            self.pdf.line(8.25*inch, 0*inch, 8.25*inch, 10.5*inch)     # right margin


    def drawStringWrap(self, x,y, text, font, fontsize, maxwidth, lineheight, position = ""):
        textlines = [text]
        i = 0
        yoffset = 0
        self.pdf.setFont(font, fontsize)
        while i < len(textlines):
            textwidth = self.pdf.stringWidth(textlines[i], font, fontsize)
            if textwidth/(1*inch) < maxwidth:
                if position == "center":
                    self.pdf.drawCentredString(x,y, textlines[i])
                elif position == "right":
                    self.pdf.drawRightString(x,y, textlines[i])
                else:
                    self.pdf.drawString(x,y, textlines[i])

                y = y - lineheight * inch
                i += 1
            else:
                splitpoint = int(len(textlines[i])/2)
                try:
                    splitpoint = textlines[i][splitpoint:].index(" ") + splitpoint
                except ValueError:
                    try:
                        splitpoint = textlines[i].rfind(" ")

                    except ValueError:
                        print "ERROR: \""+textlines[i]+"\" is too long and can't be split."
                        quit()

                textlines.insert(i+1, textlines[i][splitpoint+1:])
                textlines[i] = textlines[i][:splitpoint]
                yoffset += lineheight * inch

        return yoffset


    def drawBadge(self, pos):
        x = pos[0]
        y = pos[1]

        # Draw the event name
        if self.eventnameusefile:
            y -= 1.05*inch
            self.pdf.drawImage(self.eventname, (x-1.8*inch),y, width=3.75*inch, height=0.43*inch, mask='auto')
        else:
            self.pdf.setFont("Helvetica-Bold", 27)
            y -= 0.8*inch
            self.pdf.drawCentredString(x,y, self.eventname)

        # Draw the attendees name
        self.pdf.setFont("Helvetica-Bold", 29)
        y -= 0.60*inch
        yoffset = self.drawStringWrap((x-0.0*inch),y, fullname, "Helvetica", 29, 4.0, 0.35, "center")
        y -= yoffset

        # Draw the attendees institution
        self.pdf.setFont("Helvetica", 23)
        y -= 0.35*inch
        yoffset = self.drawStringWrap(x,y, institution, "Helvetica", 23, 4.0, 0.35, "center")
        y -= yoffset

        # Draw the QR code
        y -= 2.325*inch
        if fullname.strip() != "":
            self.pdf.drawInlineImage(imgfile, (x-1.1*inch),y, width=2.2*inch, height=2.2*inch)

        if (pos[1] - y)/inch > 5.4:
            print "ERROR: badge for \""+fullname+"\" contains too much information"
            quit()

        # Draw the hashtag
        self.pdf.setFont("Helvetica-Bold", 17)
        y = pos[1] - 5.4*inch
        self.pdf.drawCentredString(x,y, self.hashtag)
        return


    def drawSchedule(self,pos):
        x,y = pos
        y -= 0.60*inch
        self.pdf.setFont("Helvetica", 11)

         # Draw the mini schedule.
        
        self.pdf.setLineWidth(0.5)
        self.pdf.setDash([1,0], 0)
        lineheight = 0.15
        fontsize = 10

        prevroom1   = ""
        prevroom2   = ""
        prevroom3   = ""

        #open the schedulefile
        self.csvfile
        schedulefp = open(self.csvfile, 'rb')
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
            yoffset = max(yoffset, self.drawStringWrap((x-1.62*inch),y, starttime, "Helvetica", fontsize, 0.4, lineheight, "right"))
            self.pdf.drawString(x,y, self.eventname)

            # Draw the titles of the presentations.
            # Compare to the previous row.
            if room2 == "" and room3 == "":
                if room1 != prevroom1:
                    yoffset = max(yoffset, self.drawStringWrap((x-1.55*inch),y, room1, fonttype, fontsize, 3.5, lineheight))
            else:
                if room1 != prevroom1:
                    yoffset = max(yoffset, self.drawStringWrap((x-1.5*inch),y, room1, fonttype, fontsize, 1.0, lineheight))
                if room2 != prevroom2:
                    yoffset = max(yoffset, self.drawStringWrap((x-0.3*inch),y, room2, fonttype, fontsize, 1.0, lineheight))
                if room3 != prevroom3:
                    yoffset = max(yoffset, self.drawStringWrap((x+1.0*inch),y, room3, fonttype, fontsize, 1.0, lineheight))

            # Draw the vertical lines in this row
            if room1 != "":
                self.pdf.line((x-1.6*inch), (y + lineheight * inch), (x-1.6*inch), (y-yoffset-2))
            if room2 != "":
                self.pdf.line((x-0.35*inch), (y + lineheight * inch), (x-0.35*inch), (y-yoffset-2))
            if room3 != "":
                self.pdf.line((x+0.95*inch), (y + lineheight * inch), (x+0.95*inch), (y-yoffset-2))

            y -= yoffset

            # Draw the horizontal lines above this row.
            # Unless its the first row
            y -= 2
            if index != 0:
                above = (y + yoffset + (lineheight * inch) + 2)
                self.pdf.line((x-2.0*inch), above, (x-1.6*inch), above)
                if room1 != prevroom1 or room1 == "":
                    self.pdf.line((x-1.6*inch), above, (x-0.35*inch), above)
                if room2 != prevroom2 or room2 == "":
                    self.pdf.line((x-0.35*inch), above, (x+0.95*inch), above)
                if room3 != prevroom3 or room3 == "":
                    self.pdf.line((x+0.95*inch), above, (x+2.0*inch), above)

            # Set this row as previous.
            prevroom1   = room1
            prevroom2   = room2
            prevroom3   = room3

        # Draw a line after the schedule.
        self.pdf.line((x-2.0*inch), y, (x+2.0*inch), y)

        #All day events
        y -= 1.65 * lineheight * inch
        self.drawStringWrap((x-1.9*inch),y, "The VR Experience: Sign up for sesssions in Room 125", fonttype, fontsize, 4.0, lineheight)
        y -= lineheight * inch
        self.drawStringWrap((x-1.9*inch),y, "8:30am - 4:15pm", fonttype, fontsize, 4.0, lineheight)
        return


    def getPosition(self, pagepos):
        if self.badgeformat == "B475":
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

        elif self.badgeformat == "B628":
            if pagepos == 0:
                pos = 2.25*inch, 6.5*inch
            elif pagepos == 1:
                pos = 6.25*inch, 6.5*inch
        return pos


if __name__ == "__main__":
    #----------------------------
    # Main Program Begins
    #----------------------------
    qrbm = qrbadgemaker()

    # Parse options and parameters.
    for index, arg in enumerate(sys.argv):
        if arg == "--schedule":
            qrbm.schedule = True

        elif arg == "--format":
            if sys.argv[index+1] == "B475":
                qrbm.badgeformat = "B475"
                qrbm.badgesperpage = 4
            elif sys.argv[index+1] == "B628":
                qrbm.badgeformat = "B628"
                qrbm.badgesperpage = 2

        elif arg == "--template":
            qrbm.drawtemplate = True

        elif arg == "--event":
            qrbm.eventname = sys.argv[index+1]

        elif arg == "--hashtag":
            qrbm.hashtag = sys.argv[index+1]

        elif os.path.splitext(arg)[1] == ".csv":
            qrbm.csvfile = arg
     
    # Validate options and parameters or display help.
    error = False
    if qrbm.csvfile == "":
        error = True
    elif qrbm.csvfile != "" and not os.path.exists(qrbm.csvfile):
        print
        print "ERROR: File '"+qrbm.csvfile+"' not found."
        print
        error = True

    if error:
        displayHelp()
        quit()


    # Split off the filename for output.
    filename = os.path.splitext(qrbm.csvfile)[0]

    # Check if eventname is an image file.
    if os.path.exists(qrbm.eventname):
        qrbm.eventnameusefile = True
    else:
        qrbm.eventnameusefile = False

    # Initialize the PDF for output
    qrbm.pdf = canvas.Canvas(filename+".pdf", pagesize=letter)
    inch = inch * 1.05  # Adjust what defines an inch.
    qrbm.pdf.translate((-3.0/16*inch), (-9.0/32*inch))

    pagepos = 0
    badgecount = 0

    if qrbm.schedule:
        # Draw the schedule on each badge
        for pagepos in range(0, qrbm.badgesperpage):
            pos = qrbm.getPosition(pagepos)
            qrbm.drawSchedule(pos)
            badgecount += 1
        if qrbm.drawtemplate:
            qrbm.drawTemplateLines()
        qrbm.newpage()

    else:
        # Read the user data and draw each badge on the page.
        namesfp = open(qrbm.csvfile, 'rb')
        namesdata = csv.reader(namesfp)
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

                pos = qrbm.getPosition(pagepos)

                qrbm.drawBadge(pos)

                badgecount += 1
                pagepos += 1
                if pagepos >= qrbm.badgesperpage:
                    if qrbm.drawtemplate:
                        qrbm.drawTemplateLines()
                    qrbm.newpage()
                    pagepos = 0

        if pagepos != 0:
            if qrbm.drawtemplate:
                qrbm.drawTemplateLines()
            qrbm.newpage()

        os.remove(imgfile)

    print
    print str(badgecount)+" Badges created in "+filename+".pdf"
    print
    
