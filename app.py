# Streamlit App for Excel Processing (UK Spelling)

import streamlit as st
from supabase import create_client, Client # Client might not be directly used here but good for context
from utils.auth import init_supabase_client, sign_up_with_email, sign_in_with_email, sign_in_with_phone, verify_phone_otp, sign_out
from etl import append_group_sheet # Import the ETL function
import io # For handling bytes data for download

st.set_page_config(layout="wide", page_title="Excel Enrichment Service")

# Initialise Supabase client
if "supabase" not in st.session_state:
    st.session_state.supabase = init_supabase_client()

supabase = st.session_state.supabase

# Initialise user state
if "user" not in st.session_state:
    st.session_state.user = None
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "processed_file_bytes" not in st.session_state:
    st.session_state.processed_file_bytes = None

# --- Main App Logic ---
st.title("Excel File Enrichment Service")

if not supabase:
    st.error("Failed to connect to authentication service. Please check your Supabase credentials in secrets.toml.")
    st.stop()

# Check if user is already logged in
if not st.session_state.user:
    try:
        current_session = supabase.auth.get_session()
        if current_session and current_session.user:
            st.session_state.user = current_session.user
    except Exception as e:
        pass # Fail silently

if st.session_state.user:
    st.sidebar.write(f"Logged in as: {st.session_state.user.email or st.session_state.user.phone}")
    if st.sidebar.button("Sign Out"):
        sign_out(supabase)
        st.session_state.processed_file_bytes = None # Clear processed file on sign out

    # --- File Upload and Processing Section ---
    st.header("Upload and Process Your Excel File")

    uploaded_file = st.file_uploader("Choose an .xlsx file", type=["xlsx"])
    months_for_prorating = st.number_input(
        "Number of months YTD for prorating annual budgets", 
        min_value=1, 
        max_value=12, 
        value=9, 
        step=1,
        help="Enter the number of months to use for prorating any annual budget figures in your file (1-12)."
    )

    if uploaded_file is not None:
        if st.button("Process File"):
            st.session_state.processed_file_bytes = None # Reset before processing
            file_bytes = uploaded_file.getvalue()
            with st.spinner("Processing your file, please wait..."):
                try:
                    enriched_workbook_bytes = append_group_sheet(file_bytes, months_for_prorating)
                    if enriched_workbook_bytes:
                        st.session_state.processed_file_bytes = enriched_workbook_bytes
                        st.success("File processed successfully! You can now download the enriched workbook.")
                    else:
                        st.error("Failed to process the Excel file. The ETL function returned no data. Please check the file format and required sheets (TTW, MRP, TPO, WFA, PTC). Check console logs if running locally for more details from the ETL script.")
                except Exception as e:
                    st.error(f"An error occurred during file processing: {e}")
                    # Potentially log e to a more persistent store or show more details if in debug mode
    
    if st.session_state.processed_file_bytes:
        st.download_button(
            label="Download Enriched Workbook (.xlsx)",
            data=st.session_state.processed_file_bytes,
            file_name=f"{uploaded_file.name.split(".xlsx")[0]}_enriched.xlsx" if uploaded_file else "enriched_workbook.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.sidebar.title("User Authentication")
    auth_tab_email, auth_tab_phone = st.sidebar.tabs(["Email Login/Sign-up", "NZ Mobile Login"])

    with auth_tab_email:
        st.subheader("Login or Sign Up with Email")
        email_action = st.radio("Choose action:", ("Login", "Sign Up"), horizontal=True, key="email_action")

        with st.form("email_auth_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(email_action)

            if submitted:
                if not email or not password:
                    st.warning("Please enter both email and password.")
                else:
                    if email_action == "Login":
                        sign_in_with_email(supabase, email, password)
                    elif email_action == "Sign Up":
                        sign_up_with_email(supabase, email, password)

    with auth_tab_phone:
        st.subheader("Login with NZ Mobile (SMS OTP)")
        phone_number_nz = st.text_input("NZ Mobile Number (e.g., 0212345678)", placeholder="02X XXX XXXX", key="phone_input")

        if not st.session_state.otp_sent:
            if st.button("Send OTP", key="send_otp_btn"):
                if phone_number_nz:
                    full_phone_number = phone_number_nz
                    if not phone_number_nz.startswith("+"):
                        if phone_number_nz.startswith("0"):
                            full_phone_number = "+64" + phone_number_nz[1:]
                        else:
                            full_phone_number = "+64" + phone_number_nz
                    
                    st.session_state.full_phone_number = full_phone_number
                    if sign_in_with_phone(supabase, full_phone_number):
                        st.session_state.otp_sent = True
                        st.rerun()
                else:
                    st.warning("Please enter your NZ mobile number.")
        else:
            st.info(f"OTP sent to {st.session_state.get("full_phone_number", "your phone")}. Please enter it below.")
            with st.form("otp_verify_form"):
                otp_token = st.text_input("Enter OTP")
                otp_submitted = st.form_submit_button("Verify OTP")

                if otp_submitted:
                    if otp_token and st.session_state.get("full_phone_number"):
                        verify_phone_otp(supabase, st.session_state.full_phone_number, otp_token)
                        st.session_state.otp_sent = False 
                        st.session_state.pop("full_phone_number", None)
                        st.rerun()
                    else:
                        st.warning("Please enter the OTP.")
            if st.button("Resend OTP / Change Number"):
                st.session_state.otp_sent = False
                st.session_state.pop("full_phone_number", None)
                st.rerun()

    st.markdown("--- ")
    st.info("Please log in or sign up to use the Excel enrichment service.")

# Instructions for Supabase credentials
st.sidebar.markdown("""
### Supabase Configuration
To use this application, you need to configure your Supabase credentials.
Create a `secrets.toml` file in the `.streamlit` directory of this project with the following content:

```toml
[connections.supabase]
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_anon_key"
```
Replace `your_supabase_url` and `your_supabase_anon_key` with your actual Supabase project URL and anon key.
""")

