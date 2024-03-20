### 03/20/2024 test sending a message to GREX slack channel #candidates

import requests

webhook_url = "https://hooks.slack.com/services/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"

message = {
    "text": "Gotta get the bread and milk!"
}

response = requests.post(webhook_url, json=message)

print(response.status_code)