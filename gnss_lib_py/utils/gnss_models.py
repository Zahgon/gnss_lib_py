"""Model GNSS measurements and measurement corrections.

Functions to generate expected measurements, simulate noisy mesurements,
and estimate pseudorange corrections (clock corrections, ionospheric and
tropospheric delays) for given receiver states and time.
"""

__authors__ = "Ashwin Kanhere, Bradley Collicott"
__date__ = "17 Jan, 2023"

import warnings

import numpy as np
from numpy.random import default_rng

import gnss_lib_py.utils.constants as consts
from gnss_lib_py.utils.coordinates import ecef_to_geodetic, ecef_to_el_az
from gnss_lib_py.navdata.navdata import NavData
from gnss_lib_py.utils.time_conversions import gps_millis_to_tow
from gnss_lib_py.utils.sv_models import find_visible_ephem, _extract_pos_vel_arr, \
                        find_sv_location, find_sv_states, \
                        find_visible_sv_posvel, _sort_ephem_measures, \
                        _filter_ephemeris_measurements
from gnss_lib_py.utils.ephemeris_downloader import DEFAULT_EPHEM_PATH
from gnss_lib_py.navdata.operations import loop_time, sort, concat, find_wildcard_indexes

def add_measures(measurements, state_estimate,
                 ephemeris_path = DEFAULT_EPHEM_PATH, iono_params=None,
                 pseudorange=True, doppler=True, corrections=True,
                 delta_t_dec = -2):
    """Estimate measurements and add to given navdata with rx measures.

    Given measurements that were received, containing time, GNSS ID and
    SV ID, computes estimated pseudorange and doppler measurements and
    adds them to the input navdata.

    If the input navdata does not contain SV positions and velocities,
    which are required to estimate measurements, they are added to the
    navdata as well.

    Must contain rows:
    * :code:`gps_millis`
    * :code:`gnss_id`
    * :code:`sv_id`

    To use previously computed SV states, provide following rows:
    * :code:`x_sv_m`
    * :code:`y_sv_m`
    * :code:`z_sv_m`
    * :code:`vx_sv_mps`
    * :code:`vy_sv_mps`
    * :code:`vz_sv_mps`

    To estimate the expected measurements, the receiver state is needed.
    This state is stored in `state_estimate` and must contain the
    following rows
    * :code:`x_rx*_m`
    * :code:`y_rx*_m`
    * :code:`z_rx*_m`
    * :code:`vx_rx*_mps`
    * :code:`vy_rx*_mps`
    * :code:`vz_rx*_mps`


    Parameters
    ----------
    measurements : gnss_lib_py.navdata.navdata.NavData
        Received measurements for which SV states are required. Must
        contain `gps_millis`, `gnss_id`, and `sv_id` fields.
    state_estimate : gnss_lib_py.navdata.navdata.NavData
        Estimate for receiver states --- ECEF x, y, and z positions in meters,
        ECEF x, y, and z velocities in meters, clock bias in meters, and
        the clock drift in meters per second --- stored in a NavData instance.
    ephemeris_path : string or path-like
        Location where ephemeris files are stored. Files will be
        downloaded if they don't exist for the given date and constellation.
    iono_params : np.ndarray
        Parameters to calculate the ionospheric delay in pseudoranges.
    pseudorange : bool
        Flag on whether pseudoranges are to be calculated and used or not.
    doppler : bool
        Flag on whether doppler measurements are to be calculated and
        used or not.
    corrections : bool
        Flag on whether pseudorange corrections are to be calculated and
        used or not.
    delta_t_dec : int
        Decimal places after which times are considered as belonging to
        the same discrete time interval.

    Notes
    -----
    In some cases, such as when using derived versions of the collected
    data from the Google Decimeter Challenge, the measurements contain
    state estimates in the same data structure as the received measurements.
    In such a case, a separate `state_estimate` can be generated using
    the particular class' method for generating a separate `state_estimate`.
    """
    pass


def simulate_measures(gps_millis, state, noise_dict=None, ephem=None,
                      sv_posvel=None, rng=None, el_mask=5.):
    """Simulate GNSS pseudoranges and doppler measurements given receiver state.

    Measurements are simulated by finding satellites visible from the
    given position (in state), computing the expected pseudorange and
    doppler measurements for those satellites, corresponding to the given
    state, and adding Gaussian noise to these expected measurements.

    Parameters
    ----------
    gps_millis : int
        Time at which measurements are needed, measured in milliseconds
        since start of GPS epoch [ms].
    state : gnss_lib_py.navdata.navdata.NavData
        NavData instance containing state i.e. 3D position, 3D velocity,
        receiver clock bias and receiver clock drift rate at which
        measurements have to be simulated.
        Must be a single state (single column)
    noise_dict : dict
        Dictionary with pseudorange ('prange_sigma') and doppler noise
        ('doppler_sigma') standard deviation values in [m] and [m/s].
        If None, uses default values `prange_sigma=6` and
        `doppler_sigma=1`.
    ephem : gnss_lib_py.navdata.navdata.NavData
        NavData instance containing satellite ephemeris parameters for a
        particular time of ephemeris. Use None if not available and using
        SV positions directly instead.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Precomputed positions of satellites, set to None if not available.
    rng : np.random.Generator
        A random number generator for sampling random noise values.
    el_mask: float
        The elevation mask above which satellites are considered visible
        from the given receiver position. Only visible sate.

    Returns
    -------
    measurements : gnss_lib_py.navdata.navdata.NavData
        Pseudorange (label: `prange`) and doppler (label: `doppler`)
        measurements with satellite SV. Gaussian noise is added to
        expected measurements to simulate stochasticity.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Satellite positions and velocities (same as input if provided).

    """
    pass


def expected_measures(gps_millis, state, ephem=None, sv_posvel=None):
    """Compute expected pseudoranges and doppler measurements given receiver
    states.

    Parameters
    ----------
    gps_millis : int
        Time at which measurements are needed, measured in milliseconds
        since start of GPS epoch [ms].
    state : gnss_lib_py.navdata.navdata.NavData
        NavData instance containing state i.e. 3D position, 3D velocity,
        receiver clock bias and receiver clock drift rate at which
        measurements have to be simulated.
        Must be a single state (single column)
    ephem : gnss_lib_py.navdata.navdata.NavData
        NavData instance containing satellite ephemeris parameters for a
        particular time of ephemeris, use None if not available and
        using position directly.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Precomputed positions of satellites (if available).

    Returns
    -------
    measurements : gnss_lib_py.navdata.navdata.NavData
        Pseudorange (label: `prange`) and doppler (label: `doppler`)
        measurements with satellite SV. Also contains SVs and gps_tow at
        which the measurements are simulated.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Satellite positions and velocities (same as input if provided).
    """
    pass


def _extract_state_variables(state):
    """Extract position, velocity and clock bias terms from state.

    Parameters
    ----------
    state : gnss_lib_py.navdata.navdata.NavData
        NavData containing state values i.e. 3D position, 3D velocity,
        receiver clock bias and receiver clock drift rate at which
        measurements will be simulated.

    Returns
    -------
    rx_ecef : np.ndarray
        3x1 Receiver 3D ECEF position [m].
    rx_v_ecef : np.ndarray
        3x1 Receiver 3D ECEF velocity.
    clk_bias : float
        Receiver clock bais [m].
    clk_drift : float
        Receiver clock drift [m/s].

    """
    pass


def calculate_pseudorange_corr(gps_millis, state=None, ephem=None, sv_posvel=None,
                                 iono_params=None):
    """Incorporate corrections in measurements.

    Incorporate clock corrections (relativistic and polynomial), tropospheric
    and ionospheric atmospheric delay corrections.

    Parameters
    ----------
    gps_millis : int
        Time at which measurements are needed, measured in milliseconds
        since start of GPS epoch [ms].
    state : gnss_lib_py.navdata.navdata.NavData
        NavData containing state values i.e. 3D position, 3D velocity,
        receiver clock bias and receiver clock drift rate at which
        measurements will be simulated.
    ephem : gnss_lib_py.navdata.navdata.NavData
        Satellite ephemeris parameters for measurement SVs, use None if
        using satellite positions instead.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Precomputed positions of satellites corresponding to the input
        `gps_millis`, set to None if not available.
    iono_params : np.ndarray
        Ionospheric atmospheric delay parameters for Klobuchar model,
        passed in 2x4 array, use None if not available.

    Returns
    -------
    tropo_delay : np.ndarray
        Estimated delay caused by the troposhere [m].
    iono_delay : np.ndarray
        Estimated delay caused by the ionosphere [m].


    Notes
    -----
    Based on code written by J. Makela.
    AE 456, Global Navigation Sat Systems, University of Illinois
    Urbana-Champaign. Fall 2017

    """
    pass


def _calculate_tropo_delay(gps_millis, rx_ecef, ephem=None, sv_posvel=None):
    """Calculate tropospheric delay

    Parameters
    ----------
    gps_millis : int
        Time at which measurements are needed, measured in milliseconds
        since start of GPS epoch [ms].
    rx_ecef : np.ndarray
        3x1 array of ECEF rx_pos position [m].
    ephem : gnss_lib_py.navdata.navdata.NavData
        Satellite ephemeris parameters for measurement SVs.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Precomputed positions of satellites, set to None if not available.

    Returns
    -------
    tropo_delay : np.ndarray
        Tropospheric corrections to pseudorange measurements [m].

    Notes
    -----
    Based on code written by J. Makela.
    AE 456, Global Navigation Sat Systems, University of Illinois
    Urbana-Champaign. Fall 2017

    """
    pass


def _calculate_iono_delay(gps_millis, iono_params, rx_ecef, ephem=None,
                          sv_posvel=None, constellation="gps"):
    """Calculate the ionospheric delay in pseudorange using the Klobuchar
    model Section 5.3.2 [1]_.

    Parameters
    ----------
    gps_millis : int
        Time at which measurements are needed, measured in milliseconds
        since start of GPS epoch [ms].
    iono_params : np.ndarray
        Ionospheric atmospheric delay parameters for Klobuchar model,
        passed in 2x4 array, use None if not available.
    rx_ecef : np.ndarray
        3x1 receiver position in ECEF frame of reference [m], use None
        if not available.
    ephem : gnss_lib_py.navdata.navdata.NavData
        Satellite ephemeris parameters for measurement SVs, use None if
        using satellite positions instead.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Precomputed positions of satellites corresponding to the input
        `gps_millis`, set to None if not available.
    constellation : string
        Constellation used for the ionospheric parameters addition.

    Returns
    -------
    iono_delay : np.ndarray
        Estimated delay caused by the ionosphere [m].

    Notes
    -----
    Based on code written by J. Makela.
    AE 456, Global Navigation Sat Systems, University of Illinois
    Urbana-Champaign. Fall 2017

    References
    ----------
    ..  [1] Misra, P. and Enge, P,
        "Global Positioning System: Signals, Measurements, and Performance."
        2nd Edition, Ganga-Jamuna Press, 2006.

    """
    pass
