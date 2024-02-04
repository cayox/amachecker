import csv
import logging

import pandas as pd


def get_delimiter(file: str) -> str:
    """Dinamically find the delimiter of `file`."""
    with open(file) as f:
        sniffer = csv.Sniffer()
        text = f.read(4096)
        f.seek(0)
        return sniffer.sniff(text).delimiter


def export_asins_from_csv(file_path: str) -> list[str]:
    """Export ASINs from a csv file.

    Looking for first column with "asin" in name

    Args:
        file_path: the path to the csv file.

    Returns:
        a list of all ASINs found.
    """
    logging.debug("Finding delimiter for %s", file_path)
    delimiter = get_delimiter(file_path)
    logging.debug("Parsing CSV %s", file_path)
    df = pd.read_csv(file_path, sep=delimiter, header=0)
    asin_col = None

    for column in df.columns:
        if "asin" in column.lower() and len(df[~df[column].isna()]) > 0:
            asin_col = column
            break

    if asin_col is None:
        raise ValueError("No asin column found")

    return df.loc[~df[asin_col].isna(), asin_col].tolist()
