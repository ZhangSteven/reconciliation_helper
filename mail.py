# coding=utf-8
# 
# send email to notify the users about the conversion and upload results.
# 

from os.path import join
import smtplib
from email.mime.text import MIMEText
from reconciliation_helper.utility import logger, get_mail_sender, \
											get_mail_recipients, \
											get_mail_subject, \
											get_mail_server, \
											get_mail_timeout



def send_notification(result, upload_result):
	"""
	Send email notification to users about the conversion and upload
	results.
	"""
	msg = MIMEText(create_msg_text(result, upload_result))
	msg['Subject'] = get_mail_subject()
	msg['From'] = get_mail_sender()
	msg['To'] = ', '.join([to.strip() for to in get_mail_recipients().split(',')])

	smtp = smtplib.SMTP(get_mail_server(), timeout=get_mail_timeout())
	smtp.send_message(msg)
	smtp.quit()



def create_msg_text(result, upload_result):
	if len(result['fail']) == 0 and len(upload_result['fail']) == 0:
		msg = 'All {0} files converted and uploaded successfully\n'.format(len(result['pass']))
	else:
		msg = 'Errors occurred during conversion or upload process\n'

	msg = msg + '\nConversion: passed {0}, failed {1}\n'.\
			format(len(result['pass']), len(result['fail']))
	for file in result['pass']:
		msg = msg + 'pass: {0}\n'.format(file)

	msg = msg + '\n'
	for file in result['fail']:
		msg = msg + 'fail: {0}\n'.format(file)

	msg = msg + '\n\nUpload: passed {0}, failed {1}\n'.\
			format(len(upload_result['pass']), len(upload_result['fail']))
	for file in upload_result['pass']:
		msg = msg + 'uploaded: {0}\n'.format(file)

	msg = msg + '\n'
	for file in upload_result['fail']:
		msg = msg + 'failed: {0}\n'.format(file)

	return msg



if __name__ == '__main__':
	"""
	For testing only.
	"""
	result = {'pass':['a_file', 'b_file'], 'fail':['c_file'], \
				'upload':[]}
	upload_result = {'pass':['1_csv'], 'fail':['2_csv']}
	send_notification(result, upload_result)