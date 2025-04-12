from abc import ABC, abstractmethod
from client_data.client_data import ClientData


class Model(ABC):
    @abstractmethod
    def predict(self, client: ClientData) -> int:
        pass


class SimpleModel(Model):
    def predict(self, client: ClientData) -> int:
        return 1
