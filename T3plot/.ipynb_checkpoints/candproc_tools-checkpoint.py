import numpy as np
import xarray
import matplotlib.pyplot as plt
import pandas as pd

from your.candidate import Candidate
from your.formats.filwriter import make_sigproc_object

def write_sigproc(fnfilout, stokesi_obj, t_start):
    """ Write a StokesI object to a .fil file 
    using the YOUR library.

    Parameters
    ----------
    fnfilout : str
        The file name of the .fil file to write to.
    stokesi_obj : xarray.DataArray
        The Stokes I data object to write.

    Returns
    -------
    None
    """
    nchans = stokesi_obj.freq.shape[0]
    foff = np.diff(stokesi_obj.freq)[0]
    fch1 = stokesi_obj.freq.values[0]
    tsamp = np.diff(stokesi_obj.time)[0] * 86400.
    sigproc_object = make_sigproc_object(
                                    rawdatafile=fnfilout,
                                    source_name="bar",
                                    nchans=nchans,
                                    foff=foff,  # MHz
                                    fch1=fch1,  # MHz
                                    tsamp=tsamp,  # seconds
                                    tstart=t_start,  # MJD
                                    src_raj=112233.44,  # HHMMSS.SS
                                    src_dej=112233.44,  # DDMMSS.SS
                                    machine_id=0,
                                    nbeams=1,
                                    ibeam=0,
                                    nbits=16,
                                    nifs=1,
                                    barycentric=0,
                                    pulsarcentric=0,
                                    telescope_id=6,
                                    data_type=0,
                                    az_start=-1,
                                    za_start=-1,)

    sigproc_object.write_header(fnfilout)
    sigproc_object.append_spectra(stokesi_obj.data, fnfilout)

def read_voltage_data(file_name, timedownsample=None,
                      freqdownsample=None):
    """ Read in the voltage data from a .nc file 
    and return it as StokesI.

    Parameters
    ----------
    file_name : str
        The file name of the .nc file with voltages
    timedownsample : int
        The factor to downsample in time
    freqdownsample : int
        The factor to downsample in frequency
    
    Returns
    -------
    stokesi : xarray.DataArray
        The Stokes I data object
    """
    ds = xarray.open_dataset(file_name, chunks={"time": 2048})

    # Create complex numbers from Re/Im
    voltages = ds["voltages"].sel(reim="real") + ds["voltages"].sel(reim="imaginary") * 1j
    # Make Stokes I by converting to XX/YY and then creating XX**2 + YY**2
    stokesi = np.square(np.abs(voltages)).astype('int32')
    stokesi = stokesi.sum(dim='pol').astype('int32')  # Summing and then converting type if necessary

    # Compute in parallel (if using Dask)
    stokesi = stokesi.compute()

    if timedownsample is not None:
        stokesi = stokesi.coarsen(time=int(timedownsample), boundary='trim').mean()
    if freqdownsample is not None:
        stokesi = stokesi.coarsen(freq=int(freqdownsample), boundary='trim').mean()

    return stokesi, ds.time.min().values, (ds.time.values.max() - ds.time.values.min())*86400 # start time in mjd, and duration of .nc file in seconds

def read_proc_fil(fnfil, dm=0, tcand=2.0, 
                  width=1, device=0, tstart=0,
                  tstop=10, ndm=32, dmtime_transform=False):
    """ Read in a filterbank file with the 
    YOUR library, dedisperse it, and return the 
    dedispsered object.

    Parameters
    ----------
    fnfil : str
        The file name of the filterbank file.
    dm : float
        The dispersion measure to dedisperse to.
    tcand : float
        The time of the candidate.
    width : float
        The width of the candidate in samples
    device : int
        The GPU device to use.
    tstart : float
        The start time of the chunk to read in seconds
    tstop : float
        The stop time of the chunk to read in seconds
    ndm : int
        The number of DMs to transform to
    dmtime_transform : bool
        Whether to transform to DM-time space

    Returns
    -------
    cand : Candidate
        The dedispersed candidate object, 
        including the original data.
    """
    cand = Candidate(
        fp=fnfil,
        dm=dm,
        tcand=tcand,
        width=width,
        label=-1,
        snr=12,
        device=device,
    )
    cand.get_chunk(tstart, tstop)
    cand.dedisperse(target="GPU")

    if dmtime_transform:
        cand.dmtime(ndm, target='GPU')

    return cand