import streamlit as st
import os
import pandas as pd
import re
import time
from amachecker.export_reader import export_asins_from_csv
from amachecker.product_page_checker import check_price_per_unit
import logging

log = logging.getLogger(__name__)


def gui():
    st.title("Amachecker")
    st.text("Check amazon product websites for their price per unit attributes.")

    export_file = st.file_uploader(
        "Upload the export (.csv or .txt with ';' as seperator)", ["csv", "txt"]
    )

    if export_file is not None:
        if not export_file:
            st.error("No export given")
            return

        with st.spinner("Checking websites ..."):
            asins = export_asins_from_csv(export_file)

        with st.spinner("Finding prices per unit ..."):
            results = check_price_per_unit(asins)

        st.title("Results")
        col1, col2 = st.columns(2)
        delay = {}
        for url, result in results.items():
            if result:
                delay[url] = result
                continue

            with col1:
                st.write(f"[{url}]({url})")
            with col2:
                st.error("No PPU found!")

        for url, result in delay.items():
            with col1:
                st.write(f"[{url}]({url})")
            with col2:
                st.success("PPU found!")
