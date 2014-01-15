# _evalTFP.py
from __future__ import division
import numpy as np

from ._evalRPoly import evalRPoly
from ._evalTF import evalTF
from ._utils import carray, restore_input_form, save_input_form
from ._constants import eps

def evalTFP(Hs, Hz, f):
    """Evaluate a CT-DT transfer function product.

    Compute the value of a transfer function product Hs*Hz at a frequency f,
    where Hs is a continuous-time TF and Hz is a discrete-time TF.

    Use this function to evaluate the signal transfer function of a
    continuous-time (CT) system. In this context ``Hs`` is the open-loop
    response of the loop filter from the ``u`` input and ``Hz`` is the
    closed-loop noise transfer function.

    .. note:: This function attempts to **cancel poles** in ``Hs`` with **zeros** in ``Hz``.

    **Parameters:**

    Hs : tuple
        Hs is a CT (SISO) TF in zpk-tuple form.

    Hz : tuple
        Hz is a DT (SISO) TF in zpk-tuple form.

    f : scalar or 1D array or sequence
        frequency values.

    **Returns:**

    H : scalar, or ndarray or sequence
        The calculated values: 

        .. math::

            H(f) = H_s(j2\\pi f)\ H_z(e^{j2\\pi f})

        ``H`` has the same form as ``f``.

    .. seealso:: 
        :func:`evalMixedTF`, a more advanced version of this function
        which is used to evaluate the individual feed-in transfer functions of
        a CT modulator.

    **Example:**

    Plot the STF of the 2nd-order CT system depicted at :func:`mapCtoD`.::

        import numpy as np
        import pylab as plt
        from scipy.signal import lti
        from pydelsigma import *
        from pydelsigma._utils import _get_zpk
        Ac = np.array([[0, 0], [1, 0]])
        Bc = np.array([[1, -1], [0, -1.5]])
        Cc = np.array([[0, 1]])
        Dc = np.array([[0, 0]])
        LFc = (Ac, Bc, Cc, Dc)
        L0c = _get_zpk((Ac, Bc[:, 0].reshape((-1, 1)), Cc, Dc[0, 0].reshape(1, 1)))
        tdac = [0, 1]
        LF, Gp = mapCtoD(LFc, tdac)
        LF = lti(*LF)
        ABCD = np.vstack((np.hstack((LF.A, LF.B)),
                          np.hstack((LF.C, LF.D))
                        ))
        H, _ = calculateTF(ABCD)
        # Yields H=(1-z^-1)^2
        f = np.linspace(0, 2, 300);
        STF = evalTFP(L0c, _get_zpk(H), f)
        plt.plot(f, dbv(STF))
        plt.ylabel("|STF| [dB]")
        plt.xlabel("frequency ($f \\\\rightarrow f_s$)")
        figureMagic((0, 2), .5, None, (-60, 0), 20, None)

    .. plot::

        import numpy as np
        import pylab as plt
        from scipy.signal import lti
        from pydelsigma import *
        from pydelsigma._utils import _get_zpk
        Ac = np.array([[0, 0], [1, 0]])
        Bc = np.array([[1, -1], [0, -1.5]])
        Cc = np.array([[0, 1]])
        Dc = np.array([[0, 0]])
        LFc = (Ac, Bc, Cc, Dc)
        L0c = _get_zpk((Ac, Bc[:, 0].reshape((-1, 1)), Cc, Dc[0, 0].reshape(1, 1)))
        tdac = [0, 1]
        LF, Gp = mapCtoD(LFc, tdac)
        LF = lti(*LF)
        ABCD = np.vstack((np.hstack((LF.A, LF.B)),
                          np.hstack((LF.C, LF.D))
                        ))
        H, _ = calculateTF(ABCD)
        # Yields H=(1-z^-1)^2
        f = np.linspace(0, 2, 300);
        STF = evalTFP(L0c, _get_zpk(H), f)
        plt.plot(f, dbv(STF))
        plt.ylabel("|STF| [dB]")
        plt.xlabel("frequency ($f \\\\rightarrow f_s$)")
        figureMagic((0, 2), .5, None, (-60, 0), 20, None)

    """

    szeros, spoles, sk = Hs
    zzeros, zpoles, zk = Hz
    # sanitize f
    form_f = save_input_form(f)
    f = carray(f)
    if not np.prod(f.shape) == max(f.shape):
        raise ValueError("The f array must have shape " + 
                         "(N,) or (N, 1) or (N, 1, 1) ...")
    f = f.reshape((-1,))
    # sanitize poles and zeros
    szeros, spoles = carray(szeros).squeeze(), carray(spoles).squeeze()
    zzeros, zzeros = carray(zzeros).squeeze(), carray(zzeros).squeeze()
    # back to business
    slim = min(0.001, max(1e-05, eps**(1./(1 + spoles.size))))
    zlim = min(0.001, max(1e-05, eps**(1./(1 + zzeros.size))))
    H = np.zeros(f.shape, dtype=np.complex128)
    w = 2*np.pi*f
    s = 1j*w
    z = np.exp(s)
    for i in range(f.shape[0]):
        wi = w[i]
        si = s[i]
        zi = z[i]
        if spoles.size == 0:
            cancel = False
        else:
            cancel = (np.abs(si - spoles) < slim)
        if not np.any(cancel):
            # wi is far from a pole, so just use the product Hs*Hz
            H[i] = evalTF(Hs, si)*evalTF(Hz, zi)
        else:
            # cancel pole(s) of Hs with corresponding zero(s) of Hz
            cancelz = np.abs(zi - zzeros) < zlim
            if np.sum(cancelz) > np.sum(cancel):
                H[i] = 0.
            else:
                if np.sum(cancelz) < np.sum(cancel):
                    H[i] = np.Inf
                else:
                    H[i] = evalRPoly(szeros, si, sk)*zi**np.sum(cancel) \
                           * evalRPoly(zzeros[~cancelz], zi, zk) \
                           / (evalRPoly(spoles[~cancel], si, 1.)  \
                              * evalRPoly(zpoles, zi, 1.))
    # return H matching the shape of f
    H = restore_input_form(H, form_f)
    return H

def test_evalTFP():
    """Test function for evalTFP"""
    #          (z-0.3)
    # H1 = ---------------
    #      (z-0.5) (z-0.9)
    H1 = (np.array([.3]), np.array([.5, .9]), 1)
    #             1
    # H2 = ---------------
    #      (z-0.3) (z-0.9)
    H2 = (np.array([]), np.array([.3, .9]), 1)
    a = evalTFP(H1, H2, .2)
    at = np.array([0.5611 + 0.1483j])
    assert np.allclose(np.array([a]), at, atol=1e-4, rtol=1e-4)
    assert np.isscalar(a)
    #          (z-0.301)
    # H1 = ---------------
    #      (z-0.5) (z-0.9)
    H1 = (np.array([.301]), np.array([.5, .9]), 1)
    #             1
    # H2 = ---------------
    #      (z-0.3) (z-0.9)
    H2 = (np.array([]), np.array([.3, .9]), 1)
    a = evalTFP(H1, H2, np.array([.2, .23, .4]))
    at = np.array([0.5610 + 0.1488j, 0.4466 + 0.0218j, 0.0632 - 0.1504j])
    assert np.allclose(a, at, atol=1e-4, rtol=1e-4)
    assert np.array([.2, .23, .4]).shape == a.shape
