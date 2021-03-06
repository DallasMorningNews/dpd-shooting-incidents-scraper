import os
import requests
import pytz

import sentry_sdk

from datetime import datetime, timedelta
from slacker import Slacker

sentry_sdk.init("https://4977e134cc214148b24587db324e7783@o101507.ingest.sentry.io/5264608")

# pull the slack token from our environment variables
slack = Slacker(os.environ.get('SLACK_TOKEN'))

# helper function to convert 12-hour time to 24-hour
def convert24(str1):
    print(str1)
    date_time_string = datetime.strptime(str1, '%H:%M:%S')
    print(date_time_string.strftime('%H:%M:%S'))
    return date_time_string.strftime('%H:%M:%S')


def perform_scrape(): 

  HEADERS = {
      'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'),
      'referer': 'https://dallasopendata.com',
      'accept-language': 'he-IL,he;q=0.8,en-US;q=0.6,en;q=0.4',
      'cache-control': 'max-age=0'
      }

  r = requests.get("https://www.dallasopendata.com/api/id/9fxf-t2tr.json?$query=select *, :id order by `date` desc limit 100", headers=HEADERS, timeout=120)

  # if our request is successful ...
  if r: 
    calls = r.json()
    # set a marker for when the scrape happened
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    # set our timezone
    local = pytz.timezone('America/Chicago')

    # set the cutoff time for six minutes prior 
    cutoff = now - timedelta(minutes = 6)

    # our alert types that we alert for
    alert_types = ['14 - Cutting', '19 - Shooting', '27 - Dead Person']

    # our empty list that we'll put any matching events into
    attachments = []

    # for each call returned in the scrape
    for call in calls:
      # pluck just the date from the date property. DPD sends an entire date_time string, but the time is always zeroed out and included in a 12-hour format on the time key
      calldate = call['date'].split('T')[0]
      
      # convert the time of the incident to 24 hour format
      # calltime = convert24(call['time'])
      # add the date and time back as a complete date_time string to the call
      call['date_time'] = calldate + 'T' + call['time']
      
      # convert the date_time string to a date_object
      calltime = datetime.strptime(call['date_time'], '%Y-%m-%dT%H:%M:%S')
      # convert that time to our local timezone (in case it isn't)
      local_calltime = local.localize(calltime)
      # convert the call back to utc to make our comparison 
      utc_calltime = local_calltime.astimezone(pytz.utc)

      # if the call happened after our cutoff time, matches our alert type, and is not already in our attachments, add it
      if utc_calltime > cutoff:
        print(call['nature_of_call'])
        if call["nature_of_call"] in alert_types:
          if not any(d['incident_number'] == call['incident_number'] for d in attachments):
            attachments.append(call)


    # for each call in the attachmenrts, send a slack message
    if len(attachments) > 0:
      # create a prefix message for our slack posting

      slackMsg = ''

      for incident in attachments: 
        
        try: 
          slackMsg = '***DPD incident report: {0}*** \n {1} \n {2} \n {3} block {4}'.format(incident['nature_of_call'], incident['time'], incident['date'].split('T')[0], incident['block'], incident['location'])
        except KeyError:
          slackMsg = '***DPD incident report: {0}*** \n {1} \n {2} \n {3}'.format(incident['nature_of_call'], incident['time'], incident['date'].split('T')[0], incident['location'])
      
        # post our message and attachments
        slack.chat.post_message(
            '#feed-dpd-incident-alerts',
            slackMsg,
            as_user=False,
            icon_emoji='cardboardbox',
            username='DPD Incident Bot'
        )
  else: 
    # if an error code is generated by our request, alert the slack channel something has gone wrong
    slack.chat.post_message(
      '#feed-dpd-incident-alerts',
      'Warning! There was an error when trying to check for new incidents. Alert the data team if this problem persists.',
      as_user=False,
      icon_emoji='cardboardbox',
      username='DPD Incident Bot'
    )


  