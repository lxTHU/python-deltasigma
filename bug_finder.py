# -*- coding: utf-8 -*-
# bug finder
"""
Testing deltasigma toolbox's function, find bug, or verify function.
"""

#%% imports package modules
# from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from deltasigma import synthesizeNTF, simulateDSM, ds_hann, calculateSNR, evalTF
from deltasigma import dbv, figureMagic, dbp

#%% 
ORDER = 6
OSR = 16
FC = 0.5
h0p5 = synthesizeNTF(order=ORDER, osr=OSR, opt=1, H_inf=1.5, f0=FC)
print(h0p5)

#%%
N = 8192
FB = int(np.ceil(N / (2. * OSR)))
ftest = np.floor(2. / 3. * FB)
u = 0.5 * np.sin(2 * np.pi * ftest * np.arange(N) / N)
v, xn, xmax, y = simulateDSM(u, h0p5)
t = np.arange(301)

#%%
plt.figure(figsize=(20, 4))
plt.step(t, u[t], 'r')
# plt.hold(True)
plt.step(t, v[t], 'g')
plt.axis([0, 300, -1.2, 1.2])
plt.xlabel('Sample Number')
plt.ylabel('u, v')
plt.title('Modulator Input & Output')
plt.grid(True)
plt.show()

#%%
f = np.linspace(0, 0.5, N / 2. + 1)
spec = np.fft.fft(v * ds_hann(N)) / (N / 4)
plt.plot(f, dbv(spec[:int(N / 2. + 1)]), 'b', label='Simulation')
figureMagic([0, 0.5], 0.05, None, [-120, 0], 20,
            None, (16, 6), 'Output Spectrum')
plt.xlabel('Normalized Frequency')
plt.ylabel('dBFS')
snr = calculateSNR(spec[2:FB + 1], ftest - 2)
plt.text(0.05, -10, 'SNR = %4.1fdB @ OSR = %d' %
         (snr, OSR), verticalalignment='center')
NBW = 1.5 / N
Sqq = 4 * evalTF(h0p5, np.exp(2j * np.pi * f)) ** 2 / 3.
# hold(True)
plt.plot(f, dbp(Sqq * NBW), 'm', linewidth=2, label='Expected PSD')
plt.text(0.49, -90, 'NBW = %4.1E x $f_s$' % NBW, horizontalalignment='right')
plt.legend(loc=4)
plt.show()
