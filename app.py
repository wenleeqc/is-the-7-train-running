from flask import Flask, render_template
from markupsafe import escape

from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

api_key = os.getenv('API_KEY')
url = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts'

headers = {'x-api-key': api_key}
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get(
    url,
    headers = headers)
feed.ParseFromString(response.content)

subway_feed = protobuf_to_dict(feed)
currData = subway_feed['entity']

trainLine = '7'
message = None
startTime = 1
endTime = None
isPlannedWork = False
currentTime = time.time()

for alert in currData:
    currAlert = alert['alert']['informed_entity'][0]
    currLine = currAlert.get('route_id', None)

    if currLine == trainLine:
        startTime = alert['alert']['active_period'][0]['start']
        if 'planned' in alert['id']:
            isPlannedWork = True
            endTime = alert['alert']['active_period'][0]['end']

        if isPlannedWork:
            if currentTime > startTime and currentTime < endTime:
                currMessage = alert['alert']['header_text']['translation'][0]['text']
                message = currMessage
                break
        else:
            if currentTime > startTime:
                currMessage = alert['alert']['header_text']['translation'][0]['text']
                message = currMessage
                break

@app.route("/")
def index():
    return render_template('index.html', message=message, trainLine=trainLine)
