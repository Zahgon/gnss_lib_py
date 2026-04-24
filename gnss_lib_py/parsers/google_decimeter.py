"""Functions to process Android measurements.

"""

__authors__ = "Ashwin Kanhere, Derek Knowles, Shubh Gupta, Adam Dai"
__date__ = "02 Nov 2021"


import os
import warnings

import numpy as np
import pandas as pd

from gnss_lib_py.navdata.navdata import NavData
from gnss_lib_py.navdata.operations import loop_time, concat, find_wildcard_indexes, interpolate
from gnss_lib_py.utils.coordinates import wrap_0_to_2pi
from gnss_lib_py.utils.coordinates import geodetic_to_ecef
from gnss_lib_py.utils.coordinates import ecef_to_geodetic
from gnss_lib_py.utils.time_conversions import unix_to_gps_millis
from gnss_lib_py.utils.time_conversions import gps_to_unix_millis
from gnss_lib_py.utils.constants import CONSTELLATION_ANDROID, QZSS_PRN_SVN

class AndroidDerived2021(NavData):
    """Class handling derived measurements from Android dataset.

    Inherits from NavData().

    Parameters
    ----------
    input_path : string or path-like
        Path to measurement csv file
    remove_timing_outliers : bool
        Flag for whether to remove measures that are too close or
        too far away in time. Code from the competition hosts used
        to implement changes. See note.

    Notes
    -----
    Removes duplicate rows using correction 5 from competition hosts
    implemented from https://www.kaggle.com/code/gymf123/tips-notes-from-the-competition-hosts/notebook
    retrieved on 10 August, 2022

    """
    def __init__(self, input_path, remove_timing_outliers=True):
        pd_df = pd.read_csv(input_path)
        # Correction 1: Mapping _derived timestamps to previous timestamp
        # for correspondance with ground truth and Raw data
        derived_timestamps = pd_df['millisSinceGpsEpoch'].unique()
        mapper = dict(zip(derived_timestamps[1:],derived_timestamps[:-1]))
        pd_df = pd_df[pd_df['millisSinceGpsEpoch'] != derived_timestamps[0]]
        pd_df["millisSinceGpsEpoch"] = pd_df["millisSinceGpsEpoch"].replace(mapper)

        # Correction 5 implemented verbatim from competition tips
        if remove_timing_outliers:
            delta_millis = pd_df['millisSinceGpsEpoch'] - pd_df['receivedSvTimeInGpsNanos'] / 1e6
            where_good_signals = (delta_millis > 0) & (delta_millis < 300)
            pd_df = pd_df[where_good_signals].copy()
            if np.all(~where_good_signals):
                warnings.warn("All data removed due to timing outliers,"
                            + " try setting remove_timing_outliers to"
                            + " False", RuntimeWarning)

        super().__init__(pandas_df=pd_df)

    def postprocess(self):
        """Android derived specific postprocessing.

        Adds corrected pseudoranges to measurements. Time step
        corrections implemented from dataset webpage [1]_ retrieved on
        10 August, 2022.

        Correlates constellation type numbers with corresponding
        constellation names. Mapping also comes from competition
        website [1]_.

        References
        ----------
        .. [1] https://www.kaggle.com/c/google-smartphone-decimeter-challenge/data

        """
        pass

    @staticmethod
    def _row_map():
        """Map of row names from loaded to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}
        """
        pass


class AndroidDerived2022(NavData):
    """Class handling derived measurements from Android dataset.

    Inherits from NavData().
    The row nomenclature for the new derived dataset has changed.
    We reflect this changed nomenclature in the _row_map() method.

    Parameters
    ----------
    input_path : string or path-like
        Path to measurement csv file

    """

    def __init__(self, input_path, **kwargs):
        super().__init__(csv_path=input_path, **kwargs)

    def postprocess(self):
        """Android derived specific postprocessing.

        Notes
        -----
        Adds corrected pseudoranges to measurements. Time step corrections
        implemented from https://www.kaggle.com/c/google-smartphone-decimeter-challenge/data
        retrieved on 10 August, 2022.
        """
        pass


    def get_state_estimate(self):
        """Extract relevant rows in a separate NavData for state estimate.

        Returns
        -------
        state_estimate : gnss_lib_py.navdata.navdata.NavData
            Instance of `NavData` containing state estimate rows present
            in the instance of `AndroidDerived2022`.
        """
        pass

    @staticmethod
    def _row_map():
        """Map of row names from loaded to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}
        """
        pass


class AndroidGroundTruth2021(NavData):
    """Class handling ground truth from Android dataset.

    Inherits from NavData().

    Parameters
    ----------
    input_path : string or path-like
        Path to measurement csv file

    """
    def __init__(self, input_path):
        super().__init__(csv_path=input_path)

        self.postprocess()

    def postprocess(self):
        """Android derived specific postprocessing for NavData()

        Notes
        -----
        Corrections incorporated from Kaggle notes hosted here:
        https://www.kaggle.com/code/gymf123/tips-notes-from-the-competition-hosts
        """
        pass

    @staticmethod
    def _row_map():
        """Map of row names from loaded ground truth to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}
        """
        pass


class AndroidGroundTruth2022(AndroidGroundTruth2021):
    """Class handling ground truth from Android dataset.

    Inherits from AndroidGroundTruth2021().
    """

    def postprocess(self):
        """Android derived specific postprocessing for NavData()

        Notes
        -----
        """
        pass

    @staticmethod
    def _row_map():
        """Map row names from loaded data to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}
        """
        pass


class AndroidDerived2023(AndroidDerived2022):
    """Class handling derived measurements from 2023 Android dataset.

    Processes the Google Smartphone Decimeter Challenge 2023 [2]_.

    Inherits from AndroidDerived2022().

    Parameters
    ----------
    input_path : string or path-like
        Path to measurement csv file

    References
    ----------
    .. [2] https://www.kaggle.com/competitions/smartphone-decimeter-2023/overview

    """

    def __init__(self, input_path):
        super().__init__(input_path=input_path,
                         dtype={'AccumulatedDeltaRangeUncertaintyMeters':np.float64})


class AndroidGroundTruth2023(AndroidGroundTruth2022):
    """Class handling ground truth from Android dataset.

    Inherits from AndroidGroundTruth2022().
    """


def solve_kaggle_baseline(navdata):
    """Convert Decimeter challenge baseline into state_estimate.

    The baseline solution was provided in 2022 and 2023, but not in 2021.

    Parameters
    ----------
    navdata : gnss_lib_py.parsers.google_decimeter.AndroidDerived2022
        Instance of the AndroidDerived2022 class.

    Returns
    -------
    state_estimate : gnss_lib_py.navdata.navdata.NavData
        Baseline state estimate.

    """
    pass

def prepare_kaggle_submission(state_estimate, trip_id="trace/phone"):
    """Converts from gnss_lib_py receiver state to Kaggle submission.

    Parameters
    ----------
    state_estimate : gnss_lib_py.navdata.navdata.NavData
        Estimated receiver position in latitude and longitude as an
        instance of the NavData class with the following
        rows: ``gps_millis``, ``lat_rx*_deg``, ``lon_rx*_deg``.
    trip_id : string
        Value for the tripId column in kaggle submission which is a
        fusion of the data and phone type.

    Returns
    -------
    output : gnss_lib_py.navdata.navdata.NavData
        NavData structure ready for Kaggle submission.

    """
    pass

def solve_kaggle_dataset(folder_path, solver, verbose=False, *args, **kwargs):
    """Run solver on all kaggle traces.

    Additional ``*args`` arguments are passed into the ``solver``
    function.

    Parameters
    ----------
    folder_path: string or path-like
        Path to folder containing all traces (e.g. full path to "train"
        or "test" directories.
    solver : function
        State estimate solver that takes an instance of
        AndroidDerived2022 and outputs a state_estimate NavData object.
        Additional ``*args`` arguments are passed into this ``solver``
        function.
    verbose : bool
        If verbose, will print each trace trajectory name and phone name
	    pair when it is solving the state estimate for that pair.

    Returns
    -------
    solution : gnss_lib_py.navdata.navdata.NavData
        Full solution submission across all traces. Can then be saved
        using submission.to_csv().

    """
    pass
