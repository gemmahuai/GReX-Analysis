### Calculate SNR

import numpy as np 
import scipy


class SNR_Tools:

    def __init__(self):
        pass

    def sigma_from_mad(self, data):
        """ Get gaussian std from median 
        aboslute deviation (MAD)
        """
        assert len(data.shape)==1, 'data should be one dimensional'

        med = np.median(data)
        mad = np.median(np.absolute(data - med))

        return 1.4826*mad, med

    def calc_snr_presto(self, data):
        """ Calculate S/N of 1D input array (data)
        after excluding 0.05 at tails
        """
        std_chunk = scipy.signal.detrend(data, type='linear')
        std_chunk.sort()
        ntime_r = len(std_chunk)
        stds = 1.148*np.sqrt((std_chunk[ntime_r//40:-ntime_r//40]**2.0).sum() /
                              (0.95*ntime_r))
        snr_ = std_chunk[-1] / stds 

        return snr_, stds

    def calc_snr_amber(self, data, thresh=3.):
        sig = np.std(data)
        dmax = (data.copy()).max()
        dmed = np.median(data)
        N = len(data)

        # remove outliers 4 times until there 
        # are no events above threshold*sigma
        for ii in range(4):
            ind = np.where(np.abs(data-dmed)<thresh*sig)[0]
            sig = np.std(data[ind])
            dmed = np.median(data[ind])
            data = data[ind]
            N = len(data)

        snr_ = (dmax - dmed)/(1.048*sig)

        return snr_

    def calc_snr_mad(self, data):
        sig, med = self.sigma_from_mad(data)

        return (data.max() - med) / sig
