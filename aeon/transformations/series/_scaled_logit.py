"""Implements the scaled logit transformation."""

__maintainer__ = []
__all__ = ["ScaledLogitSeriesTransformer"]

from copy import deepcopy
from warnings import warn

import numpy as np

from aeon.transformations.series.base import BaseSeriesTransformer


class ScaledLogitSeriesTransformer(BaseSeriesTransformer):
    r"""Scaled logit transform or Log transform.

    If both lower_bound and upper_bound are not None, a scaled logit transform is
    applied to the data. Otherwise, the transform applied is a log transform variation
    that ensures the resulting values from the inverse transform are bounded
    accordingly. The transform is applied to all scalar elements of the input array
    individually.

    Parameters
    ----------
    lower_bound : float, optional, default=None
        lower bound of inverse transform function
    upper_bound : float, optional, default=None
        upper bound of inverse transform function


    Notes
    -----
    | The scaled logit transform is applied if both upper_bound and lower_bound are
    | not None:
    |   :math:`log(\frac{x - a}{b - x})`, where a is the lower and b is the upper bound.

    | If upper_bound is None and lower_bound is not None the transform applied is
    | a log transform of the form:
    |   :math:`log(x - a)`

    | If lower_bound is None and upper_bound is not None the transform applied is
    | a log transform of the form:
    |   :math:`- log(b - x)`

    | The transform is independent of the axis, so the data can be shape
    | `` (n_timepoints, n_channels)`` (axis == 0) or
    |  ``(n_channels, n_timepoints)`` (axis ==1)

    References
    ----------
    .. [1] Hyndsight - Forecasting within limits:
        https://robjhyndman.com/hyndsight/forecasting-within-limits/
    .. [2] Hyndman, R.J., & Athanasopoulos, G. (2021) Forecasting: principles and
        practice, 3rd edition, OTexts: Melbourne, Australia. OTexts.com/fpp3.
        Accessed on January 24th 2022.
    """

    _tags = {
        "X_inner_type": "np.ndarray",
        "fit_is_empty": True,
        "capability:multivariate": True,
        "capability:inverse_transform": True,
    }

    def __init__(self, lower_bound=None, upper_bound=None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        super().__init__(axis=1)

    def _transform(self, X, y=None):
        """Transform X and return a transformed version.

        private _transform containing core logic, called from transform

        Parameters
        ----------
        X : 2D np.ndarray
            Time series of shape (n_timepoints, n_channels)
        y : Ignored argument for interface compatibility

        Returns
        -------
        transformed version of X
        """
        if self.upper_bound is not None and np.any(X >= self.upper_bound):
            warn(
                "X in ScaledLogitSeriesTransformer should not have values "
                "greater than upper_bound",
                RuntimeWarning,
            )

        if self.lower_bound is not None and np.any(X <= self.lower_bound):
            warn(
                "X in ScaledLogitSeriesTransformer should not have values "
                "lower than lower_bound",
                RuntimeWarning,
            )

        if self.upper_bound and self.lower_bound:
            X_transformed = np.log((X - self.lower_bound) / (self.upper_bound - X))
        elif self.upper_bound is not None:
            X_transformed = -np.log(self.upper_bound - X)
        elif self.lower_bound is not None:
            X_transformed = np.log(X - self.lower_bound)
        else:
            X_transformed = deepcopy(X)

        return X_transformed

    def _inverse_transform(self, X, y=None):
        """Inverse transform, inverse operation to transform.

        private _inverse_transform containing core logic, called from inverse_transform

        Parameters
        ----------
        X : 2D np.ndarray
            Data to be inverse transformed
        y : Ignored argument for interface compatibility

        Returns
        -------
        inverse transformed version of X
        """
        if self.upper_bound and self.lower_bound:
            X_inv_transformed = (self.upper_bound * np.exp(X) + self.lower_bound) / (
                np.exp(X) + 1
            )
        elif self.upper_bound is not None:
            X_inv_transformed = self.upper_bound - np.exp(-X)
        elif self.lower_bound is not None:
            X_inv_transformed = np.exp(X) + self.lower_bound
        else:
            X_inv_transformed = deepcopy(X)

        return X_inv_transformed

    @classmethod
    def _get_test_params(cls, parameter_set="default"):
        """Return testing parameter settings for the estimator.

        Parameters
        ----------
        parameter_set : str, default="default"
            Name of the set of test parameters to return, for use in tests. If no
            special parameters are defined for a value, will return `"default"` set.

        Returns
        -------
        params : dict or list of dict, default = {}
            Parameters to create testing instances of the class
            Each dict are parameters to construct an "interesting" test instance, i.e.,
            `MyClass(**params)` or `MyClass(**params[i])` creates a valid test instance.
        """
        return {"lower_bound": -(10**6), "upper_bound": 10**6}
