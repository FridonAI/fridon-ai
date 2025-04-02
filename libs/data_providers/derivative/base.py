from abc import ABC, abstractmethod


class DerivativeDataProvider(ABC):
    @abstractmethod
    def get_open_interest(self, symbol: str):
        pass

    @abstractmethod
    def get_funding_rates(self, symbol: str):
        pass

    @abstractmethod
    def get_liquidations(self, symbol: str):
        pass

    @abstractmethod
    def get_long_short_ratio(self, symbol: str):
        pass

    @abstractmethod
    def get_basis(self, symbol: str):
        pass