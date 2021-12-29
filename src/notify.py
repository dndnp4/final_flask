import boto3

from config import AWSConfig


SUBJECT = "AWS5-Project-Signup!"
BODY_TEXT = ("Player Sign-up!"
            )
BODY_HTML = """<html>
<head></head>
<body>
  <h1>AWS5-Project player Sign-up</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>AWS SES</a>
    using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>
      from AWS5 Team.</p>
</body>
</html>
            """
CHARSET = "UTF-8"

def ses_connection():
    ses = boto3.client('ses', region_name='ap-northeast-2')
    return ses

def send_email():
    ses = ses_connection()
    res = ses.send_email(
        Destination={
            'ToAddresses': [
                AWSConfig.SES_EMAIL
            ]
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            }
        },
        Source='BTC  <%s>' % (AWSConfig.SES_EMAIL),
        ConfigurationSetName=AWSConfig.SES_CONFIG_SET_NAME
    )
    print(res)
    return