"""Functions to process Android measurements.

Tested on Google Android's GNSSLogger App v3.0.6.4

Includes functionality for:
  * Fix Measurements
  * Raw Measurements
  * Accel Measurements
  * Gyro Measurements
  * Mag Measurements
  * Bearing Measurements

"""

__authors__ = "Ashwin Kanhere, Derek Knowles, Shubh Gupta, Adam Dai"
__date__ = "02 Nov 2021"


import os
import csv

import numpy as np
import pandas as pd

from gnss_lib_py.navdata.navdata import NavData
from gnss_lib_py.algorithms.snapshot import solve_wls
from gnss_lib_py.navdata.operations import loop_time
import gnss_lib_py.utils.constants as consts
from gnss_lib_py.utils.sv_models import add_sv_states
from gnss_lib_py.utils.time_conversions import get_leap_seconds
from gnss_lib_py.utils.time_conversions import unix_to_gps_millis

class AndroidRawGnss(NavData):
    """Handles Raw GNSS measurements from Android.

    Data types in the Android's GNSSStatus messages are documented on
    their website [1]_.

    Parameters
    ----------
    input_path : string or path-like
        Path to measurement csv or txt file.
    filter_measurements : bool
        Filter noisy measurements based on known conditions.
    measurement_filters : dict
        Conditions under which measurements should be filtered. An
        emptry dictionary passed into measurement_filters is
        equivalent to setting filter_measurements to False. See the
        docstring for ``filter_raw_measurements`` for details.
    remove_rx_b_from_pr : bool
        If true, removes the estimated initial receiver clock bias
        from the pseudorange values.
    verbose : bool
        If true, prints extra debugging statements.

    References
    ----------
    .. [1] https://developer.android.com/reference/android/location/GnssStatus


    """
    def __init__(self, input_path,
                 filter_measurements=True,
                 measurement_filters = {"bias_valid" : True,
                                        "bias_uncertainty" : 40.,
                                        "arrival_time" : True,
                                        "unknown_constellations" : True,
                                        "time_valid" : True,
                                        "state_decoded" : True,
                                        "sv_time_uncertainty" : 500.,
                                        "adr_valid" : True,
                                        "adr_uncertainty" : 15.
                                        },
                 remove_rx_b_from_pr = False,
                 verbose=False):

        self.verbose = verbose
        self.filter_measurements = filter_measurements
        self.measurement_filters = measurement_filters
        self.remove_rx_b_from_pr = remove_rx_b_from_pr
        pd_df = self.preprocess(input_path)
        super().__init__(pandas_df=pd_df)

    def preprocess(self, input_path):
        """Extract Raw measurements.

        Built on the first parts of make_gnss_dataframe and correct_log

        Parameters
        ----------
        input_path : string or path-like
            Path to measurement csv or txt file.

        Returns
        -------
        measurements : pd.DataFrame
            Subset of "Raw" measurements.

        """
        pass

    def postprocess(self):
        """Postprocess loaded NavData.

        Strategy for computing the arrival time was taken from an
        EUSPA white paper [2]_ and Google's source code
        Arrival time taken from [3]_.

        References
        ----------
        .. [2] https://www.euspa.europa.eu/system/files/reports/gnss_raw_measurement_web_0.pdf
        .. [3] https://github.com/google/gps-measurement-tools/blob/master/opensource/ProcessGnssMeas.m
        """
        pass

    def filter_raw_measurements(self,t_rx_secs):
        """Filter noisy measurements.

        Filter conditions are set in the ``AndroidRawGnss()``
        initialization with the ``measurement_filters`` variable. The
        general framework for measurement filters is taken from Google's
        ION GNSS+ 2023 workshop presentation [4]_. Google's
        gps-measurement-tools opensource software shows a couple of
        their implementations with example values [5]_ [6]_.

        The possible keys to include in the ``measurement_filters``
        dictionary variable include:

          * ``bias_valid`` : If true, measurements where FullBiasNanos is
            greater or equal to zero will be removed.
          * ``bias_uncertainty`` :  Any measurements will be
            re where BiasUncertaintyNanos is greater than
            the set value.
          * ``arrival_time`` : If true, measurements where the arrival time
            (``t_rx_secs``) is negative or unrealistically large will be
            removed.
          * ``unknown_constellations`` : If true, measurements with an
            unknown_constellation will be removed.
          * ``time_valid`` : If true, measurements with where TimeNanos is
            empty will be removed.
          * ``state_decoded`` : If true, will filter measurements that don't
            have the time-of-week decoded [7]_.
          * ``sv_time_uncertainty`` : Any measurements will be
            removed where ReceivedSvTimeUncertaintyNanos is greater than
            the set value.
          * ``adr_valid`` : If true, measurements where
            ``AccumulatedDeltaRangeState`` is not valid will be removed.
          * ``adr_uncertainty`` : Any measurements will be
            removed where ReceivedSvTimeUncertaintyNanos is greater than
            the set value.

        Only keys present in the ``measurement_filters`` dictionary
        will be used for the filter. For example if
        ````measurement_filters = {``bias_valid`` : True}, then only
        measurements will invalid FullBiasNanos will be filtered and no
        other measurements will be filtered.

        Parameters
        ----------
        t_rx_secs : np.ndarray
            arrival time computed in ``AndroidRawGnss.postprocess()``.

        References
        ----------
        .. [4] Michael Fu, Mohammed Khider, Frank van Diggelen, Dave
               Orendorff. "Workshop for Google Smartphone Decimeter
               Challenge (SDC) 2023-2024." ION GNSS+ 2023.
        .. [5] https://github.com/google/gps-measurement-tools/blob/master/opensource/ProcessGnssMeas.m
        .. [6] https://github.com/google/gps-measurement-tools/blob/master/opensource/SetDataFilter.m
        .. [7] https://developer.android.com/reference/android/location/GnssMeasurement#STATE_TOW_DECODED
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

class AndroidRawFixes(NavData):
    """Class handling location fix measurements from an Android log.

    Inherits from NavData().

    Parameters
    ----------
    input_path : string or path-like
        Path to measurement csv or txt file.

    """
    def __init__(self, input_path):
        pd_df = self.preprocess(input_path)
        super().__init__(pandas_df=pd_df)


    def preprocess(self, input_path):
        """Read Android raw file and produce location fix dataframe objects

        Parameters
        ----------
        input_path : string or path-like
            File location of data file to read.

        Returns
        -------
        fix_df : pd.DataFrame
            Dataframe that contains the location fixes from the log.

        """
        pass

    def postprocess(self):
        """Postprocess loaded data.

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

    @staticmethod
    def _provider_map():
        """Map to more intuitive names for fix provider.

        Returns
        -------
        provider_map : Dict
            Dictionary of the form {old_name : new_name}

        """
        pass

class AndroidRawAccel(NavData):
    """Class handling Accelerometer measurements from Android.

    Inherits from NavData().

    Parameters
    ----------
    input_path : string or path-like
        File location of data file to read.
    sensor_fields : tuple
        Names for the sensors to extract from the full log file.

    """
    def __init__(self, input_path,
                 sensor_fields=("UncalAccel","Accel")):

        self.sensor_fields = sensor_fields
        pd_df = self.preprocess(input_path)
        super().__init__(pandas_df=pd_df)

    def preprocess(self, input_path):
        """Read Android raw file and produce Accel dataframe objects.

        Parameters
        ----------
        input_path : string or path-like
            File location of data file to read.

        Returns
        -------
        measurements : pd.DataFrame
            Dataframe that contains the accel measurements from the log.

        """
        pass

    def postprocess(self):
        """Postprocess loaded data."""
        pass

    def _row_map(self):
        """Map of row names from loaded to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}

        """
        pass

class AndroidRawGyro(AndroidRawAccel):
    """Class handling Gyro measurements from Android.

    Parameters
    ----------
    input_path : string or path-like
        File location of data file to read.

    """
    def __init__(self, input_path):
        sensor_fields = ("UncalGyro","Gyro")
        super().__init__(input_path, sensor_fields=sensor_fields)

    def _row_map(self):
        """Map of row names from loaded to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}

        """
        pass

class AndroidRawMag(AndroidRawAccel):
    """Class handling Magnetometer measurements from Android.

    Parameters
    ----------
    input_path : string or path-like
        File location of data file to read.

    """
    def __init__(self, input_path):
        sensor_fields = ("UncalMag","Mag")
        super().__init__(input_path, sensor_fields=sensor_fields)

    def _row_map(self):
        """Map of row names from loaded to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}

        """
        pass

class AndroidRawOrientation(AndroidRawAccel):
    """Class handling Orientation measurements from Android.

    Parameters
    ----------
    input_path : string or path-like
        File location of data file to read.

    """
    def __init__(self, input_path):
        sensor_fields = ("OrientationDeg")
        super().__init__(input_path, sensor_fields=sensor_fields)

    def _row_map(self):
        """Map of row names from loaded to gnss_lib_py standard

        Returns
        -------
        row_map : Dict
            Dictionary of the form {old_name : new_name}

        """
        pass
