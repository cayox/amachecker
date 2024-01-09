import pandas as pd
import logging


def export_asins_from_csv(file) -> list[str]:
    df = pd.read_csv(file, sep=";")
    asin_col = None

    for column in df.columns:
        if "asin" in column.lower() and len(df[~df[column].isna()]) > 0:
            asin_col = column
            break

    if asin_col is None:
        raise ValueError("No asin column found")

    return df.loc[~df[asin_col].isna(), asin_col].tolist()


if __name__ == "__main__":
    asins = export_asins_from_csv("../export.csv")
    print(asins)
