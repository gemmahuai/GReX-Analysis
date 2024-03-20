from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import json
import sys
import os.path
import slack_sdk as slack

js = str(sys.argv[1]) # full json filename
# output_fn = str(sys.argv[2]) # output pdf filename

def get_cand(JSON):
    f = open('/home/user/zghuai/T3_monitor/test_inotify/'+JSON)
    data = json.load(f)
    tab = pd.json_normalize(data[JSON.split(".")[0]], meta=['id'])
    print(tab)
    f.close()
    return(tab)

tab = get_cand(js)
fig = plt.figure()
plt.scatter(tab['mjds'], tab['dm'], s=5)
plt.xlabel('MJD Time')
plt.ylabel('DM')
print('/home/user/zghuai/T3_monitor/grex_cand{}.pdf'.format(js.split('.')[0]))
plt.savefig('/home/user/zghuai/T3_monitor/grex_cand{}.pdf'.format(js.split('.')[0]))
print('done')




