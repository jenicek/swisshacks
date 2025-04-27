class Predictor:
    """Base predictor class"""

    def predict(self, data, *args, **kwargs):
        return self._predict(data, *args, **kwargs)

    def _predict(self, data, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")