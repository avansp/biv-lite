from biv_lite import BivFrames, BivMesh
import numpy as np
import pandas as pd


def test_gls(sample_biv: BivFrames, sample_gls: dict):
    gls = sample_biv.gls(ed_frame=0)

    assert np.allclose(gls['LV_GLS_2CH'], sample_gls['LV_GLS_2CH'], rtol=0, atol=1e-4)
    assert np.allclose(gls['LV_GLS_4CH'], sample_gls['LV_GLS_4CH'], rtol=0, atol=1e-4)
    assert np.allclose(gls['RVS_GLS_4CH'], sample_gls['RVS_GLS_4CH'], rtol=0, atol=1e-4)
    assert np.allclose(gls['RVFW_GLS_4CH'], sample_gls['RVFW_GLS_4CH'], rtol=0, atol=1e-4)

