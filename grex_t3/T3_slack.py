# post a given file to slack
# poetry run python T3_slack.py <filename>
### identify injected pulses and post all to slack


import numpy as np
import pandas as pd
import os

import inotify.adapters as ia
import os
import sys
import slack_sdk as slk


def upload_to_slack(pdffile):

    # set up slack client
    slack_file = '{0}/.config/slack_api'.format(
        os.path.expanduser("~")
    )

    # if the slack api token file is missing
    if not os.path.exists(slack_file):
        raise RuntimeError(
            "Could not find file with slack api token at {0}".format(
                slack_file
            )
        )
    # otherwise load the token file and start a webclient talking to slack
    with open(slack_file) as sf_handler:
        slack_token = sf_handler.read()
        # initialize slack client
        client = slk.WebClient(token=slack_token)
    
    # Define message parameters
    message = "New candidate plot generated!" ## add some cand details?
    
    try:
        # Upload the plot file to Slack
        response = client.files_upload(
            channels="candidates",
            file=pdffile,
            initial_comment=message
        )
        
        print("Plot uploaded to Slack:", response["file"]["permalink"])
    except slk.errors.SlackApiError as err:
        print(f"Error uploading plot to Slack: {err}")


d = pd.read_csv("/hdd/data/candidates/T2/cluster_output.csv")
dur = 200 # in the past {} min
DM = 100
want = (d['dm']>DM-4)&(d['dm']<DM+4) & ((d['mjds'].max()-d['mjds'])*24*60<dur) & (d['trigger']!='0') & (d['snr']>70)
#want = ((d['mjds'].max()-d['mjds'])*24*60<dur) & (d['snr']<300)

cad = 900 # cadence in seconds
t0 = d[want]['mjds'].values[0] # beginning time
tol = 2. # time of tolerance in seconds
N = 1
Pulse = [] # pulse candidate name
for i in range(len(d[want])):
    # print('i =', i)
    # print('  N =',N)
    dt = (d[want]['mjds'].values[i] - t0) * 86400
    # print('  dt  = ', dt)
    if dt > tol:
        if (abs(cad-dt)%cad < tol): # it is an injected pulse
            N+=1
            t0 = d[want]['mjds'].values[i]
            Pulse.append(d[want]['trigger'].values[i])
            # print('  SNR = ', d[want]['snr'].values[i])
            # print('  trigger name ', d[want]['trigger'].values[i])

# detection rate
N_inj = int(dur*60 / cad) # total number of injected pulses
r = N / N_inj
print('Detection rate is ', r)

print(Pulse)
for i in range(len(Pulse)):
    cmd = "poetry run python cand_plotter.py {}".format(Pulse[i]+".json")
    print(cmd)
    #os.system(cmd)
    file = "/hdd/data/candidates/T3/candplots/grex_cand" + Pulse[i] + ".png"
    #upload_to_slack(file)
