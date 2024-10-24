"""DummyForecaster always predicts the last value seen in training."""

from aeon.forecasting.base import BaseForecaster


class DummyForecaster(BaseForecaster):
    """Dummy forecaster always predicts the last value seen in training."""

    def __init__(self):
        """Initialize DummyForecaster."""
        self.last_value_ = None
        super().__init__()

    def _fit(self, y, exog=None):
        """Fit dummy forecaster."""
        self.last_value_ = y[-1]
        return self

    def _predict(self, y=None, exog=None):
        """Predict using dummy forecaster."""
        return self.last_value_

    def _forecast(self, y, X=None):
        """Forecast using dummy forecaster."""
        return y[-1]
