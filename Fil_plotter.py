from matplotlib import pyplot as plt
import numpy as np
from sigpyproc.readers import FilReader
import sys
import candproc_tools as ct


# read a .fil file, plot 10000 time samples at a time and move on to the next one if press enter
# (remove top and bottom of the band)

def plot(cand, t_start, t_end):

    plt.figure(figsize=(15,7))
    grid = plt.GridSpec(3, 6, wspace=0.1, hspace=0.1)
    plt.subplot(grid[0, :5])
    data_favg = np.nanmean(cand.data,axis=1,keepdims=True)
    cand.data = cand.data - np.nanmean(cand.data,axis=0)
    data_tavg = np.nanmean(cand.data,axis=0)
    time = np.linspace(t_start, t_end, cand.data.shape[0])
    plt.plot(time, (data_favg - np.nanmean(data_favg)) / np.nanstd(data_favg), lw=0.5, color='black')
    # plt.xlabel('Time (ms)')
    plt.ylabel('SNR')
    plt.xlim(t_start, t_end)
    plt.xticks([], [])
    plt.subplot(grid[1:, :5])
    vmax = np.nanmean(cand.data) + np.nanstd(cand.data)
    plt.imshow(cand.data.T, aspect='auto', vmax=vmax,  extent=(t_start, t_end, 1280, 1530), interpolation=None)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Frequency (MHz)', fontsize=12)
    plt.subplot(grid[1:, 5])
    freq = np.linspace(1280, 1530, cand.data.shape[1])
    plt.plot((data_tavg - np.nanmean(data_tavg)) / np.nanstd(data_tavg), freq, lw=0.7, color='black')# plt.xlabel('Frequency (MHz)')
    # plt.ylabel('SNR')
    plt.xlabel('SNR')
    plt.ylim(1530, 1280)
    plt.yticks([], [])
    plt.show()

    
    return

def main(fn):
    # if len(sys.argv) != 2:
    #     print("Usage: python script_name.py filename.fil")
    #     return
    
    # fn = str(sys.argv[1]) # .fil filename

    myfil = FilReader(fn)

    total_time = myfil.header.nsamples_files[0] * myfil.header.tsamp # s
    print(total_time)
    time_per_plot = 10
    start_time = 0

    while start_time < total_time:
        end_time = min(start_time + time_per_plot, total_time)
        print(start_time, end_time)
        cand = ct.read_proc_fil(fnfil = fn,
                                dm = 0,
                                tstart = start_time,
                                zero_topbottom = True,
                                tstop = end_time,
                                dmtime_transform=False,
                                )

        plot(cand, start_time, end_time)
        
        input("Press Enter to continue...")
        start_time = end_time

        del cand
    
    return

# if __name__ == "__main__":
#     main()