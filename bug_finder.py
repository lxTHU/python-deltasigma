#%%
#from __future__ import division
from deltasigma import synthesizeNTF
#from deltasigma._synthesizeNTF1 import synthesizeNTF1
#import deltasigma.synthesizeNTF as synthesizeNTF

order = 6
OSR = 16

H0 = synthesizeNTF(order,OSR,0,1.5,0.5)
print(H0)
