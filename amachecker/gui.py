import re

import streamlit as st
import os
import pandas as pd
from amachecker.export_reader import export_asins_from_csv
from amachecker.product_page_checker import check_price_per_unit
import logging

log = logging.getLogger(__name__)


def gui():
    st.title("Amachecker")
    st.subheader("Check amazon product websites for their price per unit attributes.")

    col1, col2 = st.columns([3, 1])
    pattern_valid = True
    with col1:
        pattern = st.text_input("Regex Pattern to search:", value="\d+,\d{2}€ / meter")
    if pattern:
        with col2:
            try:
                re.compile(pattern)
            except Exception:
                st.error("Pattern does not compile!")
                pattern_valid = False
            else:
                st.success("Pattern compiled successfully")

    export_file = st.file_uploader(
        "Upload your Seller central export (any .csv file with an asin column works)",
        ["csv", "txt"]
    )

    if export_file is not None:
        if not export_file:
            st.error("No export given")
            return

        if not pattern_valid:
            st.error("Regex Pattern is not valid!")
            return

        with st.spinner("Checking websites ..."):
            asins = export_asins_from_csv(export_file)

        with st.spinner("Finding prices per unit ... this may take a while ..."):

            results = check_price_per_unit(asins)

        st.title("Results")

        urls, res = list(results.keys()), list(results.values())
        asins = [os.path.basename(url)[:-5] for url in urls]
        df = pd.DataFrame({"ASIN": asins, "URL": urls, "Price per Unit found?": res})
        df = df.sort_values("Price per Unit found?")
        df = df.reset_index(drop=True)

        st.dataframe(df)
