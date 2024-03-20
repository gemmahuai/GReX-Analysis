### Using Inotify to monitor /hdd/data/voltages/
# when a new .nc file is generated, it calls the T3 plotting task, saves a pdf file, and pushes to the Slack candidates channel.

import inotify.adapters as ia
import os
import sys
import slack_sdk as slk


# Function to upload a plot to Slack
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


# Function to send a slack message (test)
def send_to_slack(message):

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
    try:
        response = client.chat_postMessage(
            channel="candidates",
            text=message
        )  
        
        print("Done", response.status_code)
    except slk.errors.SlackApiError as err:
        print(f"Error uploading plot to Slack: {err}")



def main(path):

    # initiate an inotify instance
    i = ia.Inotify()
    # add the directory to monitor to the instance
    i.add_watch(path)

    try:
        # create a test file, as a marker for the start of the monitoring process
        with open(path+'start_inotify_monitor', 'w'): 
            pass
        # loop and monitor the directory
        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event

            # print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
            #     path, filename, type_names))
            # print(filename)
            
            # if new file is created
            if type_names == ['IN_CREATE']:
                # if the filename ends with .nc
                if filename.endswith('.json'): # created a new .nc file
                    print('Created {}'.format(filename))
                    ### T3 goes here. 

                    # test with json
                    pdffile = "/home/user/zghuai/T3_monitor/grex_cand"+filename.split('.')[0]+".pdf"
                    command = "python inotify_testplot.py {}".format(filename)
                    # Execute the command using os.system()
                    print(command)
                    os.system(command)

                    ### after creating plots, upload to slack
                    upload_to_slack(pdffile)
                    # test; construct the output pdf filename here
                    # send_to_slack("Hello World! filename={}".format(pdffile))

            
    except PermissionError:
        print("Permission denied: Unable to create test file.")


if __name__ == '__main__':
    # path = "/hdd/data/candidates/T2/"
    # test
    path = "/home/user/zghuai/T3_monitor/test_inotify/"
    try:
        main(path)
    except KeyboardInterrupt:
        print('Interrupted')
        cmd = "rm " + path + "start_inotify_monitor" # remove monitoring file
        os.system(cmd)
        sys.exit(0)

