# -*- coding: utf-8 -*-
# bug finder
"""Testing deltasigma toolbox's function, find bug, or verify function.
"""

# %%
# from __future__ import division
from deltasigma import synthesizeNTF
# import deltasigma as ds
# from deltasigma._synthesizeNTF1 import synthesizeNTF1
# import deltasigma.synthesizeNTF as synthesizeNTF


H0 = synthesizeNTF(order=6, osr=16, opt=0, H_inf=1.5, f0=0.5)
print(H0)
