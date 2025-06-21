import json
import os
import streamlit as st

json_path = r"C:\Users\krish\Downloads\Document _Extraction\Project\all_invoices_data.json"

def load_all_data():
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_all_data(all_data, new_data, file_name):
    # Add 'image' key (filename) to new_data
    new_data["image"] = file_name

    existing_index = next(
        (i for i, d in enumerate(all_data) if d.get("image") == file_name),
        None
    )

    if existing_index is not None:
        # File already exists, do NOT add or save
        st.session_state["new_file_added"] = False
    else:
        # New file: add new_data and save
        all_data.append(new_data)
        st.session_state["new_file_added"] = True

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

    return all_data




