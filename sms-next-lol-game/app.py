import os

import requests
import json
from flask import Flask, request
from dateutil import parser

app = Flask(__name__)

CLICKSEND_USERNAME = 'username'
CLICKSEND_API_KEY = 'password'

@app.route("/", methods=['POST'])
def receive_sms():
    incoming_body = request.values.get('Body', '').strip()  # Get the text message body
    from_number = request.values.get('From', '')  # Get the sender's phone number

    # Search for the league in the upcoming matches
    league_name = incoming_body.lower()  # Convert to lowercase for case-insensitive matching

    # Filter upcoming matches by league name
    match_found = False
    for match in upcoming:
        if league_name in match['league'].lower():  # Match league name

            match_time = parser.parse(match['startTime'])
            formatted_time = match_time.strftime("%a, %b %d at %I:%M %p")
            message = (
                f"Next match in {match['league']}:\n"
                f"{match['teams'][0]} vs {match['teams'][1]}\n"
                f"Time: {formatted_time}"
            )
            match_found = True
            break

    if not match_found:
        message = f"No upcoming match found for '{league_name}'. Please try another league."

    # Send the response as an SMS
    send_sms(message, from_number)
    return "Message sent via ClickSend", 200



@app.route("/upcoming", methods=['GET'])
def get_upcoming_matches():
    return json.dumps(upcoming), 200, {"Content-Type": "application/json"}


def send_sms(body, to_number):
    sms_data = {
        "messages": [
            {
                "source": "python",
                "body": body,
                "to": to_number,
                "from": "InfoSMS"
            }
        ]
    }

    response = requests.post(
        "https://rest.clicksend.com/v3/sms/send",
        auth=(CLICKSEND_USERNAME, CLICKSEND_API_KEY),
        headers={"Content-Type": "application/json"},
        data=json.dumps(sms_data)
    )

    return response.status_code, response.text




url = "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-US" # <- This is publicly available
headers = {
    "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
}

response = requests.get(url, headers=headers)
data = response.json()

events = data['data']['schedule']['events']

upcoming = []

for event in events:
    if event['state'] == 'unstarted' and 'match' in event:
        match = {
            "matchId": event['match']['id'],
            "startTime": event['startTime'],
            "league": event['league']['name'],
            "teams": [team['name'] for team in event['match']['teams']]
        }
        upcoming.append(match)

print(json.dumps(upcoming, indent=2))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run()