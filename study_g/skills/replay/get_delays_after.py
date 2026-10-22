"""Replay example for the none-identity skill: hera_pspec src/hera_pspec/utils.py::get_delays
at commit c1b46e7 (before) and after merge f1235c7 of PR #485 (HERA-Team/hera_pspec)."""
import numpy as np


def get_delays(freqs, n_dlys=None):
    """
    Return an array of delays, tau, corresponding to the bins of the delay
    power spectrum given by frequency array.

    Parameters
    ----------
    freqs : ndarray of frequencies in Hz

    n_dlys : number of delay bins, optional
        Default: None, which then assumes that the number of bins is
        equal to the number of frequency channels.

    Returns
    -------
    delays : array_like
        Delays, tau. Units: seconds.
    """
    Delta_nu = np.median(np.diff(freqs))
    n_freqs = freqs.size

    if n_dlys is None:  # assume that n_dlys = n_freqs if not specified
        n_dlys = n_freqs

    # Calculate the delays
    delay = np.fft.fftshift(np.fft.fftfreq(n_dlys, d=Delta_nu))

    return delay
