from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    """
    Base class for all trading strategies.

    generate_weights receives closing prices up to and including the current
    date (no lookahead) and returns a dict {ticker: weight} where weights are
    in [0, 1] and sum to at most 1.  Any remainder is held as cash.
    """

    @abstractmethod
    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        """
        Parameters
        ----------
        prices : pd.DataFrame
            Historical closing prices indexed by date, columns are tickers.
            Contains data up to and including current_date.
        current_date : datetime-like
            The date for which to generate weights.

        Returns
        -------
        dict[str, float]
            {ticker: target_weight}, weights in [0,1], sum <= 1.
        """
        ...

    def __repr__(self):
        return self.__class__.__name__
