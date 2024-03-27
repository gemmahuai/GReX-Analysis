### 03/27/2024
### Using Inotify to monitor /hdd/data/candidates/T2
### when a new .json file is created, it calls the T3 plotting task, saves a pdf file, and pushes to the Slack candidates channel.
### consider multiple triggers given a single .nc file

import inotify.adapters as ia
import os
import sys
import slack_sdk as slk
import time
import logging
import cand_plotter


# poetry_project_dir = os.environ.get('POETRY_PROJECT_DIR')
# if poetry_project_dir is None:
#     print("Error: POETRY_PROJECT_DIR environment variable is not set.")
#     sys.exit(1)

# ##Borrowed from Liam's run_clear_disks.py
# logfile = '/home/user/zghuai/GReX-T3/services/T3_Plotting.log'
# env_dir = "/home/user/zghuai/GReX-T3/T3/" 
# mon_dir = "/hdd/data/voltages/" # monitoring dir

#------------------------------------------------------------------------------------
# local machine
logfile = "/Users/gemmahuai/Desktop/CalTech/GReX/GReX-Analysis/T3plot/"
env_dir = "/Users/gemmahuai/Desktop/CalTech/GReX/GReX-Analysis/T3plot/"
mon_dir = "/Users/gemmahuai/Desktop/CalTech/GReX/GReX-Analysis/T3plot/test_T3/"
nc_dir = "/hdd/data/voltages/"

# Configure the logger
logging.basicConfig(filename=logfile,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logging.info('Starting the monitoring and T3-plotting service')


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

    """
    Monitors when a new .json file is created;
    Locate the corresponding .nc file in the voltage directory;
        if there's one, do the original calculation
        elif cand MJD is in the time range of the previous .nc file (need a pointer for each .nc file in the previous layer)
            plot candidate (need to modify cand_plotter.py)
            (input .json and .nc separately, cand name in .png)
    """

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
                # if the filename ends with .json
                if filename.endswith('.json'): # created a new .json file
                    c = filename.split('.')[0].split('/')[-1].split('-')[-1] # candidate ID
                    tab = cand_plotter.get_cand(c+".json") # candidate json table
                    
                    ### if a corresponding .nc file is created
                    if os.path.isfile(nc_dir+"grex_dump-"+c+".nc")==True:

                        logging.info(f"New NetCDF file created, waiting to plot.")
                        print('Created {}'.format(filename))
                        ### T3 goes here. 
                        filename_json = c+".json"
                        print('filename = ', filename_json)

                        os.chdir(env_dir)

                        time.sleep(40)

                        try: 
                            v = "/hdd/data/voltages/grex_dump-"+c+".nc" # voltage file
                            fn_tempfil = "/hdd/data/candidates/T3/candplots/intermediate.fil" # output temporary .fil
                            fn_outfil = f"/hdd/data/candidates/T3/candfils/cand{c}.fil" # output dedispersed candidate .fil
                            (stokesi, T0) = cand_plotter.get_stokesi(v)
                            (cand, dur) = cand_plotter.gen_cand(fn_tempfil, fn_outfil, tab, stokesi, T0)

                            cand_plotter.plot_grex(cand, T0, dur, tab, c+".json") 
                            logging.info("Done with cand_plotter.py")

                            cmd = "rm {}".format(fn_tempfil)
                            print(cmd)
                            os.system(cmd)
                            logging.info("Successfully plotted the canidate!")
                        except Exception as e:
                            logging.error("Error plotting candidates: %s", str(e))

                        # cmd = "poetry run python cand_plotter.py {}".format(filename_json)
                        # print(cmd)
                        # try:
                        #     os.system(cmd)
                        #     logging.info(f"Candidate plot grex_cand{filename_json.split('.')[0]}.pdf successfully created!")
                        # except Exception as e:
                        #     logging.error("Error plotting candidates using cand_plotter.py : %s", str(e))


                        pdffile = "/hdd/data/candidates/T3/candplots/grex_cand"+filename_json.split('.')[0]+".png"
                        print("saved in ", pdffile)

                        # test with json
                        # pdffile = "/home/user/zghuai/T3_monitor/grex_cand"+filename.split('.')[0]+".pdf"
                        # command = "python inotify_testplot.py {}".format(filename)
                        # # Execute the command using os.system()
                        # print(command)
                        # os.system(command)

                        try:
                            upload_to_slack(pdffile) # upload to Slack #candidates channel
                            logging.info(f"Successfully posted to Slack #candidates!")
                        except Exception as e:
                            logging.error("Error uploading candidate plot to Slack: %s", str(e))
                        logging.info("DONE")

                        # test; construct the output pdf filename here
                        # send_to_slack("Hello World! filename={}".format(pdffile))
                        cand_nc = nc_dir+"grex_dump-"+c+".nc" # save the filename of the current .nc file 

                    ### no .nc file created but cand MJD in the time range of the previous nc file 
                    elif (stokesi.time.max().values>cand['mjds']): 
                        logging.info(f"The current candidate {c} is in the previous NetCDF file {cand_nc}, waiting to plot.")
                        print('Created {}'.format(filename))

                        ### T3 goes here. 
                        filename_json = c+".json"
                        print('filename = ', filename_json)

                        os.chdir(env_dir)

                        time.sleep(40)

                        try: 
                            v = cand_nc # voltage file
                            fn_tempfil = "/hdd/data/candidates/T3/candplots/intermediate.fil" # output temporary .fil
                            fn_outfil = f"/hdd/data/candidates/T3/candfils/cand{c}.fil" # output dedispersed candidate .fil
                            # (stokesi, T0) = cand_plotter.get_stokesi(v) # from the previous one
                            (cand, dur) = cand_plotter.gen_cand(fn_tempfil, fn_outfil, tab, stokesi, T0)

                            cand_plotter.plot_grex(cand, T0, dur, tab, c+".json") 
                            logging.info("Done with cand_plotter.py")

                            cmd = "rm {}".format(fn_tempfil)
                            print(cmd)
                            os.system(cmd)
                            logging.info("Successfully plotted the candidate!")
                        except Exception as e:
                            logging.error("Error plotting candidates: %s", str(e))

                        pdffile = "/hdd/data/candidates/T3/candplots/grex_cand"+filename_json.split('.')[0]+".png"
                        print("saved in ", pdffile)

                        try:
                            upload_to_slack(pdffile) # upload to Slack #candidates channel
                            logging.info(f"Successfully posted to Slack #candidates!")
                        except Exception as e:
                            logging.error("Error uploading candidate plot to Slack: %s", str(e))
                        logging.info("DONE")


    except PermissionError:
        logging.error("Permission denied: Unable to create inotify test file.")

    except Exception as e:
        logging.error("An error occurred: %s", str(e))


if __name__ == '__main__':
    try:
        main(mon_dir)
    except KeyboardInterrupt:
        print('Interrupted')
        cmd = "rm " + mon_dir + "start_inotify_monitor" # remove monitoring file
        os.system(cmd)
        sys.exit(0)

    

