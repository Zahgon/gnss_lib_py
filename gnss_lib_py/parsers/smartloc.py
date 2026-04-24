"""Functions to process TU Chemnitz SmartLoc dataset measurements.

"""

__authors__ = "Ashwin Kanhere, Derek Knowles"
__date__ = "02 Apr 2023"

import numpy as np

from gnss_lib_py.navdata.navdata import NavData
from gnss_lib_py.navdata.operations import loop_time
from gnss_lib_py.utils.coordinates import LocalCoord, geodetic_to_ecef, wrap_0_to_2pi
from gnss_lib_py.utils.time_conversions import tow_to_gps_millis


class SmartLocRaw(NavData):
    """Class handling raw measurements from SmartLoc dataset [1]_.

    The SmartLoc dataset is a GNSS dataset from TU Chemnitz
    Dataset is available on their website [2]_. Inherits from NavData().

    References
    ----------
    .. [1] Reisdorf, Pierre, Tim Pfeifer, Julia Bressler, Sven Bauer,
           Peter Weissig, Sven Lange, Gerd Wanielik and Peter Protzel.
           The Problem of Comparable GNSS Results – An Approach for a
           Uniform Dataset with Low-Cost and Reference Data. Vehicular.
           2016.
    .. [2] https://www.tu-chemnitz.de/projekt/smartLoc/gnss_dataset.html.en#Home


    """
    def __init__(self, input_path):
        """TU Chemnitz raw specific loading and preprocessing.

        Should input path to RXM-RAWX.csv file.

        Parameters
        ----------
        input_path : string or path-like
            Path to measurement csv file

        """

        super().__init__(csv_path=input_path, sep=";")

    def postprocess(self):
        """TU Chemnitz raw specific postprocessing

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

def remove_nlos(smartloc_raw):
    """Remove NLOS and 'no information' measurements from SmartLoc.

    The dataset's paper [3]_ says the following about their NLOS
    classification process:
    "The NovAtel receiver is also able to provide raw measurement
    (pseudorange) information like the u-blox receiver. The
    u-blox receiver provide information about all received satellite
    signals. The NovAtel receiver seems to exclude some satellites
    in harsh environments, which might be affected by NLOS.
    NovAtel used for receiving a Pinwheel antenna and internally
    different algorithms. Hence, we use this information to build a
    NLOS detection based on different satellites availabilities in
    both receivers. Therefore, we remember the last received set
    of satellites from NovAtel and time of data. When we receive
    in next step a set of satellites from u-blox, we compare the
    availability of each satellite and time span since the last update
    from the NovAtel. If the time span is too high or the satellite
    was never seen before, the pseudorange measurement or satellite
    marked as NLOS. In the other case, the measurement marked
    as LOS. This approach gives a hint for the type of LOS or
    NLOS of a given measurement and we export this information
    to complete the datasets."

    Parameters
    ----------
    smartloc_raw : gnss_lib_py.navdata.navdata.NavData
        Instance of NavData containing SmartLoc data

    Returns
    -------
    smartloc_los : gnss_lib_py.navdata.navdata.NavData
        Instance of NavData containing only LOS labeled measurements

    References
    ----------
    .. [3] Reisdorf, Pierre, Tim Pfeifer, Julia Bressler, Sven Bauer,
           Peter Weissig, Sven Lange, Gerd Wanielik and Peter Protzel.
           The Problem of Comparable GNSS Results – An Approach for a
           Uniform Dataset with Low-Cost and Reference Data. Vehicular.
           2016.

    """
    smartloc_los = smartloc_raw.where('NLOS (0 == no, 1 == yes, 2 == No Information)',
                        0, 'eq')
    return smartloc_los

def calculate_gt_ecef(smartloc_raw):
    """Calculate ground truth positions in ECEF.

    Parameters
    ----------
    smartloc_raw : gnss_lib_py.navdata.navdata.NavData
        Instance of NavData containing SmartLoc data

    Returns
    -------
    smartloc_los : gnss_lib_py.navdata.navdata.NavData
        Instance of NavData containing GT ECEF positions in meters.

    """
    llh = smartloc_raw[['lat_rx_gt_deg', 'lon_rx_gt_deg', 'alt_rx_gt_m']]
    rx_ecef = geodetic_to_ecef(llh)
    smartloc_raw = smartloc_raw.copy()
    smartloc_raw['x_rx_gt_m'] = rx_ecef[0, :]
    smartloc_raw['y_rx_gt_m'] = rx_ecef[1, :]
    smartloc_raw['z_rx_gt_m'] = rx_ecef[2, :]
    return smartloc_raw

def calculate_gt_vel(smartloc_raw):
    """Calculate ground truth velocity and acceleration in ECEF.

    Parameters
    ----------
    smartloc_raw : gnss_lib_py.navdata.navdata.NavData
        Instance of NavData containing SmartLoc data

    Returns
    -------
    smartloc_los : gnss_lib_py.navdata.navdata.NavData
        Instance of NavData containing GT ECEF velocity and acceleration
        in meters per second and meters per second^2.

    """
    llh_origin = smartloc_raw[['lat_rx_gt_deg', 'lon_rx_gt_deg', 'alt_rx_gt_m'] , 0]
    ned_frame = LocalCoord.from_geodetic(llh_origin.reshape([3,1]))
    vel_acc = {'vx_rx_gt_mps' : [],
                'vy_rx_gt_mps' : [],
                'vz_rx_gt_mps' : [],
                'ax_rx_gt_mps2' : [],
                'ay_rx_gt_mps2' : [],
                'az_rx_gt_mps2' : []}
    for _, _, measure_frame in loop_time(smartloc_raw,'gps_millis', \
                                                        delta_t_decimals = -2):
        yaw = measure_frame['heading_rx_gt_rad', 0]
        vel_gt = measure_frame['v_rx_gt_mps', 0]
        acc_gt = measure_frame['a_rx_gt_mps2', 0]
        vel_ned = np.array([[np.cos(yaw)*vel_gt], [np.sin(yaw)*vel_gt], [0.]])
        acc_ned = np.array([[np.cos(yaw)*acc_gt], [np.sin(yaw)*acc_gt], [0.]])
        vel_ecef = ned_frame.ned_to_ecefv(vel_ned)
        acc_ecef = ned_frame.ned_to_ecefv(acc_ned)
        vel_acc['vx_rx_gt_mps'].extend(np.repeat(vel_ecef[0, 0], len(measure_frame)))
        vel_acc['vy_rx_gt_mps'].extend(np.repeat(vel_ecef[1, 0], len(measure_frame)))
        vel_acc['vz_rx_gt_mps'].extend(np.repeat(vel_ecef[2, 0], len(measure_frame)))
        vel_acc['ax_rx_gt_mps2'].extend(np.repeat(acc_ecef[0, 0], len(measure_frame)))
        vel_acc['ay_rx_gt_mps2'].extend(np.repeat(acc_ecef[1, 0], len(measure_frame)))
        vel_acc['az_rx_gt_mps2'].extend(np.repeat(acc_ecef[2, 0], len(measure_frame)))
    smartloc_raw = smartloc_raw.copy()
    for row, values in vel_acc.items():
        smartloc_raw[row] = values
    return smartloc_raw
