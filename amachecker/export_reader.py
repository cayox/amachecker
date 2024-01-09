import logging

import pandas as pd

import csv


def get_delimiter(file_path, bytes=4096):
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter


def export_asins_from_csv(file) -> list[str]:
    logging.debug("Finding delimiter for %s", file.name)
    delimiter = get_delimiter(file.name)
    logging.debug("Parsing CSV %s", file.name)
    df = pd.read_csv(file, sep=delimiter)
    asin_col = None

    for column in df.columns:
        if "asin" in column.lower() and len(df[~df[column].isna()]) > 0:
            asin_col = column
            break

    if asin_col is None:
        raise ValueError("No asin column found")

    return df.loc[~df[asin_col].isna(), asin_col].tolist()
