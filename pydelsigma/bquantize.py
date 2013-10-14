import numpy as np
from pydelsigma.constants import eps
from pydelsigma.utils import empty, mfloor

def bquantize(x, nsd=3, abstol=eps, reltol=10*eps):
	"""y = bquantize(x,nsd=3,abstol=eps,reltol=10*eps)
	Bidirectionally quantize a n by 1 vector x to nsd signed digits, 
	Terminate early if the error is less than the specified tolerances.
	y is a list of instances with the same length as x and the 
	following attributes:
	* y[i].val is the quantized value in floating-point form,
	* y[i].csd is a 2-by-nsd (or less) matrix containing
	  the powers of two (first row) and their signs (second row).
	
	See also bunquantize.m.
	"""

	n = x.shape[0] if hasattr(x, 'shape') else len(x)
	#q = np.zeros((2*n, nsd)) in the original source #rep?
	y = [empty() for i in range(n)]
	offset = -np.log2(0.75)

	for i in range(n):
		xp = x[i]
		y[i].val = 0.
		y[i].csd = np.zeros((2,0), dtype='int16')
		for j in range(nsd):
			error = np.abs(y[i].val - x[i])
			if error <= abstol and error <= np.abs(x[i])*reltol: #rep? in the orig: or
				break
			p = mfloor(np.log2(np.abs(xp)) + offset)
			p2 = 2**p
			sx = np.sign(xp)
			xp = xp - sx*p2
			y[i].val = y[i].val + sx*p2
			addme = np.array((p, sx)).reshape((2, 1))
			y[i].csd = np.concatenate((y[i].csd, addme), axis=1)
	return y
	
def test_bquantize():
	import scipy.io, pkg_resources
	x = np.linspace(-10, 10, 101)
	y = bquantize(x)
	yval = [yi.val for yi in y]
	ycsd = [yi.csd for yi in y]
	fname = pkg_resources.resource_filename(__name__, "test_data/test_bquantize.mat")
	s = scipy.io.loadmat(fname)['s']
	mval = []
	mcsd = []
	for i in range(s.shape[1]):
		mval.append(float(s[0, i][0]))
		mcsd.append(s[0, i][1])
	for i in range(len(mval)):
		assert np.allclose(mval[i], yval[i], atol=1e-8, rtol=1e-5)
		mcsd[i].shape == ycsd[i].shape
		if not 0 in ycsd[i].shape:
			assert np.allclose(mcsd[i], ycsd[i], atol=1e-8, rtol=1e-5)
	
if __name__ == '__main__':
	test_bquantize()
