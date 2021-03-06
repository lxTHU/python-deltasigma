# -*- coding: utf-8 -*-
# bug finder
"""
Testing deltasigma toolbox's function, find bug, or verify function.
"""

#%% imports package modules
# from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from deltasigma import (calculateSNR, dbp, dbv, ds_hann, evalTF, figureMagic,
                        simulateDSM, synthesizeNTF)

#%% 
ORDER = 6
OSR = 16
FC = 0.5
h0p5 = synthesizeNTF(order=ORDER, osr=OSR, opt=0, H_inf=1.5, f0=FC)
print(h0p5)

#%%
NS = 16384
FB = int(np.ceil(NS / (2. * OSR)))
# ftest = np.floor(2. / 3. * FB)  #for LPF_DSM
ftest = NS//4 - np.floor(1. / 8. * FB) #for HPF_DSM
input_cos = 0.4 * np.sin(2 * np.pi * ftest * np.arange(NS) / NS)
output_DSM, xn, xmax, y = simulateDSM(input_cos, h0p5)
t = np.arange(301)

#%%
plt.figure(figsize=(12, 3))
plt.step(t, input_cos[t], 'r')
plt.step(t, output_DSM[t], 'g')
plt.axis([0, 300, -1.2, 1.2])
plt.xlabel('Sample Number')
plt.ylabel('input_cos, output_DSM')
plt.title('Modulator Input & Output')
plt.grid(True)
plt.show()
# plt.hold(True)

#%%
f = np.linspace(0, 0.5, NS / 2. + 1)
spec = np.fft.fft(output_DSM * ds_hann(NS)) / (NS / 4)
plt.plot(f, dbv(spec[:int(NS / 2. + 1)]), 'b', label='Simulation')
figureMagic([0, 0.5], 0.05, None, [-140, 0], 20, None, (16, 6), 'Output Spectrum')
plt.xlabel('Normalized Frequency')
plt.ylabel('dBFS')
snr = calculateSNR(spec[2:FB + 1], ftest - 2) #for LPF_DSM
# snr = calculateSNR(spec[N//4-FB:N//4], ftest, 4) #for HPF_DSM
plt.text(0.05, -10, 'SNR = %4.1fdB @ OSR = %d' %(snr, OSR), verticalalignment='center')
NBW = 1.5 / NS
Sqq = 4 * evalTF(h0p5, np.exp(2j * np.pi * f)) ** 2 / 3.
plt.plot(f, dbp(Sqq * NBW), 'm', linewidth=2, label='Expected PSD')
plt.text(0.49, -90, 'NBW = %4.1E x $f_s$' % NBW, horizontalalignment='right')
plt.legend(loc=4)
plt.show()

#%% output data to files
# np.savetxt('DacDsmOut.txt', output_DSM, fmt='%d')
