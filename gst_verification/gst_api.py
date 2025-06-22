import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def verify_gst(vendor_gstin):
    headers = {
        "content-type": "application/json",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "gst-return-status.p.rapidapi.com"
    }
    gst_api_url = f"https://gst-return-status.p.rapidapi.com/free/gstin/{vendor_gstin}"
    gst_response = requests.get(gst_api_url, headers=headers)

    if gst_response.status_code != 200:
        st.error("Error fetching GST details from API.")
        return None

    gst_info = gst_response.json().get("data", {})
    if not gst_info:
        st.error("GST details not found in API response.")
        return None

    return gst_info


def customer_gst(customer_gstin):
    headers = {
        "content-type": "application/json",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "gst-return-status.p.rapidapi.com"
    }
    gst_api_url = f"https://gst-return-status.p.rapidapi.com/free/gstin/{customer_gstin}"
    gst_response = requests.get(gst_api_url, headers=headers)

    if gst_response.status_code != 200:
        st.error("Error fetching GST details from API.")
        return None

    gst_info = gst_response.json().get("data", {})
    if not gst_info:
        st.error("GST details not found in API response.")
        return None

    return gst_info
