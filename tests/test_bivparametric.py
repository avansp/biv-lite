from biv_lite import BivParametric, BivFrames, BivMesh
import numpy as np


def test_BivParametric(sample_biv: BivFrames):
    """
    Tests the functionality and consistency of the BivParametric class when provided with
    BivFrames input. The function checks whether interpolation results in consistent
    BivMesh instances at certain parameter values, verifies that times are normalized,
    and ensures the volume curves remain consistent after interpolation.

    Args:
        sample_biv: Instance of BivFrames to serve as the input for initializing
            the BivParametric object and testing the interpolation capabilities.
    """
    bp = BivParametric(sample_biv)

    # bp.biv_frames must not refer to the original sample_biv object
    assert not(bp.biv_frames is sample_biv)

    # test if bp(0.0) == bp(1.0)
    bp0 = bp(0.0)
    bp1 = bp(1.0)
    assert isinstance(bp0, BivMesh)
    assert isinstance(bp1, BivMesh)
    assert np.allclose(bp0.control_points, bp1.control_points)
    assert np.allclose(bp0.nodes, bp1.nodes)
    assert np.array_equal(bp0.materials, bp1.materials)

    # check if time is normalised
    ts = bp.biv_frames.frames
    assert bp.biv_frames.is_normalised_time()

    # check if volume curves are almost equal after interpolation at knot values
    biv_interp = bp(ts)
    assert isinstance(biv_interp, BivFrames)

    src_vol = sample_biv.volumes()
    interp_vol = biv_interp.volumes()

    assert all([np.allclose(src_vol[k], interp_vol[k]) for k in src_vol.keys()])
