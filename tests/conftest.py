import pytest
from pathlib import Path
import pandas as pd
import numpy as np
from biv_lite import BivFrames


@pytest.fixture(scope="function")
def sample_volumes() -> dict:
    """
    A fixture to provide sample volume data for testing purposes. This fixture reads
    a CSV file containing left and right ventricular volume data, filters it for a
    specific test case, and prepares the data for further processing. The CSV is
    assumed to be organized with frames as rows and various volume metrics as columns.

    Args:
        None

    Returns:
        dict: A dictionary containing the following keys, each mapping to an array
        of corresponding data:
            - 'lv_vol': Left ventricular volumes.
            - 'lvm': Left ventricular mass.
            - 'rv_vol': Right ventricular volumes.
            - 'rvm': Right ventricular mass.
            - 'lv_epivol': Left ventricular epicardial volumes.
            - 'rv_epivol': Right ventricular epicardial volumes.

    Raises:
        AssertionError: If the frame numbers in the CSV file are not sequential
        starting from 0.
    """
    vol_file = Path("tests") / "sample_frames" / "lvrv_volumes.csv"
    df = pd.read_csv(vol_file)
    df = df[df['name'] == "sample_frames"].sort_values(by='frame')

    assert np.array_equal(df['frame'].to_numpy(), np.arange(df.shape[0]))

    return {
        'lv_vol': df['lv_vol'].to_numpy(),
        'lvm': df['lvm'].to_numpy(),
        'rv_vol': df['rv_vol'].to_numpy(),
        'rvm':df['rvm'].to_numpy(),
        'lv_epivol': df['lv_epivol'].to_numpy(),
        'rv_epivol': df['rv_epivol'].to_numpy()
    }


@pytest.fixture(scope="function")
def sample_biv() -> BivFrames:
    """
    Creates and returns a sample `BivFrames` instance for testing purposes.

    This fixture is used to provide a sample `BivFrames` object created from
    frame files located in the "sample_frames" directory under the "tests"
    folder. The files are matched using the specified naming pattern.

    Args:
        None

    Returns:
        BivFrames: An instance of `BivFrames` created using the specified folder
        and file pattern.
    """
    return BivFrames.from_folder(Path("tests") / "sample_frames", pattern="*_Model_Frame_*.txt")

@pytest.fixture(scope="function")
def sample_gls() -> dict:
    """
    A fixture to return Global Longitudinal Strain (GLS) data from a CSV file.

    Reads GLS measurements from a CSV file located at 'tests/sample_frames/gls.csv',
    filters for rows where the 'name' column equals "sample_frames", and sorts by frame number.

    Returns:
        dict: A dictionary containing GLS values for different cardiac views:
            - 'lv_gls_2ch' (numpy.ndarray): Left Ventricle GLS in 2-chamber view
            - 'lv_gls_4ch' (numpy.ndarray): Left Ventricle GLS in 4-chamber view
            - 'rvs_gls_4ch' (numpy.ndarray): Right Ventricle Strain GLS in 4-chamber view
            - 'rvfw_gls_4ch' (numpy.ndarray): Right Ventricle Free Wall GLS in 4-chamber view

    Raises:
        AssertionError: If frame numbers are not sequential starting from 0.
    """
    gls_file = Path("tests") / "sample_frames" / "gls.csv"
    df = pd.read_csv(gls_file)
    df = df[df['name'] == "sample_frames"].sort_values(by='frame')

    assert np.array_equal(df['frame'].to_numpy(), np.arange(df.shape[0]))

    return {
        'lv_gls_2ch': df['lv_gls_2ch'].to_numpy(),
        'lv_gls_4ch': df['lv_gls_4ch'].to_numpy(),
        'rvs_gls_4ch': df['rvs_gls_4ch'].to_numpy(),
        'rvfw_gls_4ch': df['rvfw_gls_4ch'].to_numpy()
    }

