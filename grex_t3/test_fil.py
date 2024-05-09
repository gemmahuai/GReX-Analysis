import your
import numpy as np
from matplotlib import pyplot as plt
import candproc_tools as ct
from your.formats.filwriter import make_sigproc_object

fn_vol = "/hdd/data/voltages/grex_dump-240507aaeb.nc"
dt = 8.192e-6
(stokesi, T0, dur) = ct.read_voltage_data(fn_vol, timedownsample=16, freqdownsample=None, verbose=True, nbit='uint16')
print(stokesi.shape)
print(stokesi.time.values[1])

mm = 10000
window_width = 18000
out_data = stokesi[(mm-window_width//2):(mm+window_width//2), :]
print(out_data.shape)


# t_start=T0+(mm-window_width//2)*dt/86400

# print(out_data[0].dtype)

# nchans = out_data.freq.shape[0]
# foff = np.diff(out_data.freq)[0]
# fch1 = out_data.freq.values[0]
# tsamp = np.diff(out_data.time)[0] * 86400.
# sigproc_object = make_sigproc_object(
#                                 rawdatafile="test.fil",
#                                 source_name="bar",
#                                 nchans=nchans,
#                                 foff=foff,  # MHz
#                                 fch1=fch1,  # MHz
#                                 tsamp=tsamp,  # seconds
#                                 tstart=t_start,  # MJD
#                                 src_raj=112233.44,  # HHMMSS.SS
#                                 src_dej=112233.44,  # DDMMSS.SS
#                                 machine_id=0,
#                                 nbeams=1,
#                                 ibeam=0,
#                                 nbits=16,
#                                 nifs=1,
#                                 barycentric=0,
#                                 pulsarcentric=0,
#                                 telescope_id=6,
#                                 data_type=0,
#                                 az_start=-1,
#                                 za_start=-1,)

# sigproc_object.write_header("test.fil")
# sigproc_object.append_spectra(out_data.data, "test.fil")