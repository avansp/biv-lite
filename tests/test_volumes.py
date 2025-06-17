from biv_lite import BivFrames
import numpy as np


def test_lvrv_volumes(sample_biv: BivFrames, sample_volumes: dict):
    """Testing if LVRV volumes & masses are equal with biv-me"""
    vols = sample_biv.volumes()

    assert np.allclose(vols['LV_ENDO'], sample_volumes['lv_vol'], equal_nan=True)
    assert np.allclose(vols['RV_ENDO'], sample_volumes['rv_vol'], equal_nan=True)
    assert np.allclose(vols['LV_EPI'], sample_volumes['lv_epivol'], equal_nan=True)
    assert np.allclose(vols['RV_EPI'], sample_volumes['rv_epivol'], equal_nan=True)

    # compare masses
    assert np.allclose(vols['LVM'], sample_volumes['lvm'], equal_nan=True)
    assert np.allclose(vols['RVM'], sample_volumes['rvm'], equal_nan=True)
