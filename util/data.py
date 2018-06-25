import pandas as pd
import numpy as np


def fill(series):
    if isinstance(series, pd.Series):
        return series.replace([np.inf, -np.inf], np.nan).ffill().bfill()
    elif isinstance(series, np.ndarray):
        return pd.Series(series).replace(
                     [np.inf, -np.inf], np.nan
                    ).ffill().bfill().values
    else:
        return series
