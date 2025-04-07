from biv_lite.biv_frames import perinterp
import numpy as np
import numpy.testing as npt

def test_periodic_interpolation():
    # define the samples
    xs = np.linspace(0.0, 1.0, 14)

    f_sin = lambda x: np.sin(2 * x * np.pi)
    ys = f_sin(xs)
    fi_sin = perinterp(xs[:-1],ys[:-1], k=3)
    yi = fi_sin(xs)
    npt.assert_almost_equal(yi[0], yi[-1])
    npt.assert_almost_equal(yi, ys)

    f_sincos = lambda x: 1.7 * np.sin(2 * x * np.pi) * np.cos(2 * x * np.pi)
    ys = f_sincos(xs)
    fi_sincos = perinterp(xs[:-1], ys[:-1], k=3)
    yi = fi_sincos(xs)
    npt.assert_almost_equal(yi[0], yi[-1])
    npt.assert_almost_equal(yi, ys)

    f_sin2 = lambda x: 0.3 + np.square(np.sin(2 * x * np.pi))
    ys = f_sin2(xs)
    fi_sin2 = perinterp(xs[:-1], ys[:-1], k=3)
    yi = fi_sin2(xs)
    npt.assert_almost_equal(yi[0], yi[-1])
    npt.assert_almost_equal(yi, ys)


