import smtplib, pprint
from email.mime.text import MIMEText
from time import gmtime, strftime
from socket import gethostname

# Just a function that sends the results to a given e-mail address.
# This expects a mail server to be running on localhost by default!
def send_email(address, results, mailserver='localhost', formatter=pprint.pprint):
	me = "marky@" + gethostname()
	you = address

	timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	msg = MIMEText(formatter(results))

	msg['Subject'] = "marky: Experiment completed at " + timestamp
	msg['From'] = me 
	msg['To'] = you 
	
	try:
		s = smtplib.SMTP(mailserver)
		s.sendmail(me, [you], msg.as_string())
		s.quit()
	except Exception:
		print "ERROR: Failed to send email!"
		return
	print "EMAIL: Sent e-mail to " + address + " at " + timestamp + "."
