import os
import re
from pdf2image import convert_from_path
from PIL import Image
from google import generativeai as genai
import streamlit as st
from dotenv import load_dotenv


api_key = os.getenv("GOOGLE_API_KEY")
assert api_key is not None, "GOOGLE_API_KEY is not set in Railway!"

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_invoice_data(uploaded_file=None, upload_option=None):
    extracted_text = ""
    vendor_gstin = None
    customer_gstin = None
    response1 = ""

    # UI for upload
    if uploaded_file is None and upload_option is None:
        upload_option = st.radio("Choose upload type:", ["PDF Invoice", "Image Invoice"])
        if upload_option == "PDF Invoice":
            uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        else:
            uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        return uploaded_file, upload_option

    if uploaded_file:
        if upload_option == "PDF Invoice":
            # Save PDF temporarily
            temp_pdf_dir = "temp_dir"
            os.makedirs(temp_pdf_dir, exist_ok=True)
            temp_pdf_path = os.path.join(temp_pdf_dir, uploaded_file.name)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Convert first page to image
            images = convert_from_path(temp_pdf_path)
            first_page = images[0]

            # Main response with all invoice data
            response = model.generate_content([
                "Extract all the details from the Invoice",
                first_page
            ])

            # Structured extraction
            response1 = model.generate_content([
                """Extract the following detail:
                
                - Seller  or vendorName
                - Customer or Buyer Name
                - GST Number of the Seller
                
                Return them in the following format:
                
               1. Seller Company Name:  <name> 

               2. Customer Company Name:  <name>  

               3. GST No of Seller:  <gst number>
                """,
                first_page
            ])
            response2 = model.generate_content([
                """Extract the following details:
                
                - Seller Name or vendor Name
                - Customer  or Buyer Name
                - GST Number of the Customer or Buyer
                
                Return them in the following format:

               1. Seller Company Name: <name> 

               2. Customer Company Name: <name>  

               3. GST No of customer: <gst number>
                """,
                first_page
            ])

            extracted_text = response.text
            structured_text1 = response1.text
            structured_text2 = response2.text
            os.remove(temp_pdf_path)

        else:  # Image Invoice
            # Save image temporarily
            temp_img_path = f"temp_{uploaded_file.name}"
            with open(temp_img_path, "wb") as f:
                f.write(uploaded_file.read())

            image = Image.open(temp_img_path)
            st.image(image, caption="Uploaded Invoice Image", use_column_width=True)

            response = model.generate_content([
                "Extract all the details from the Invoice.",
                image
            ])
            response1 = model.generate_content([
                """Extract the following details:
                
                - Seller or Vendor Name
                - Customer or Buyer Name
                - GST Number of the Seller or vendor
                
                Return them in the following format:

               1. Seller Company Name: <name> 

               2. Customer Company Name: <name>  

               3. GST No of Seller: <gst number>
                """,
                image
            ])
            response2 = model.generate_content([
                """Extract the following details:
                
                - Seller or Vendor Name
                - Customer or Buyer Name 
                - GST Number of the customer or Buyer
                
                Return them in the following format:

               1. Seller Company Name: <name> 

               2. Customer Company Name: <name>  

               3. GST No of customer: <gst number>
                """,
                image
            ])

            extracted_text = response.text
            structured_text1 = response1.text
            structured_text2 =response2.text
            os.remove(temp_img_path)

        # Extract GSTIN from structured text using regex
        gst_match1= re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b", structured_text1)
        gst_match2= re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b", structured_text2)

        if gst_match1 :
            vendor_gstin = gst_match1.group()
        if gst_match2 :
            customer_gstin = gst_match2.group()

        extracted_data = {
            "image": uploaded_file.name,
            "details": extracted_text,
        }


        return extracted_data, vendor_gstin , response1 , customer_gstin, response2
