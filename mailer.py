import smtplib, json
from email.mime.text import MIMEText
from time import gmtime, strftime
from socket import gethostname

def send_email(address, results):
	me = "marky@" + gethostname()
	you = address

	timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	msg = MIMEText(json.dumps(results))

	msg['Subject'] = "marky: Experiment completed at " + timestamp
	msg['From'] = me 
	msg['To'] = you 
	
	try:
		s = smtplib.SMTP('localhost')
		s.sendmail(me, [you], msg.as_string())
		s.quit()
	except Exception:
		print "ERROR: Failed to send email!"
		return
	print "EMAIL: Sent e-mail to " + address + " at " + timestamp + "."


