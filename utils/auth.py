# Supabase Authentication Utilities (UK Spelling)

import streamlit as st
from supabase import create_client, Client

# Function to initialise the Supabase client
def init_supabase_client():
    """Initialises and returns the Supabase client."""
    try:
        supabase_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        supabase_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error initialising Supabase client: {e}")
        return None

# Placeholder for email sign-up
def sign_up_with_email(supabase: Client, email: str, password: str):
    """Signs up a new user with email and password."""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Sign-up successful! Please check your email to verify your account.")
            return response.user
        elif response.error:
            st.error(f"Sign-up failed: {response.error.message}")
            return None
    except Exception as e:
        st.error(f"An unexpected error occurred during sign-up: {e}")
        return None

# Placeholder for email sign-in
def sign_in_with_email(supabase: Client, email: str, password: str):
    """Signs in an existing user with email and password."""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            st.success("Sign-in successful!")
            st.session_state.user = response.user
            st.rerun()
            return response.user
        elif response.error:
            st.error(f"Sign-in failed: {response.error.message}")
            return None
    except Exception as e:
        st.error(f"An unexpected error occurred during sign-in: {e}")
        return None

# Placeholder for phone (SMS OTP) sign-in
def sign_in_with_phone(supabase: Client, phone: str):
    """Initiates sign-in with phone number (SMS OTP)."""
    try:
        # Ensure phone number is in E.164 format, e.g., +64212345678 for NZ
        if not phone.startswith("+"):
            st.warning("Please ensure your phone number includes the country code (e.g., +64 for New Zealand).")
            return False
        response = supabase.auth.sign_in_with_otp({"phone": phone})
        if response.error:
            st.error(f"Failed to send OTP: {response.error.message}")
            return False
        else:
            st.info("OTP sent to your phone. Please enter it below.")
            return True # Indicates OTP was sent
    except Exception as e:
        st.error(f"An unexpected error occurred while sending OTP: {e}")
        return False

# Placeholder for verifying phone OTP
def verify_phone_otp(supabase: Client, phone: str, token: str):
    """Verifies the OTP sent to the user's phone."""
    try:
        response = supabase.auth.verify_otp({"phone": phone, "token": token, "type": "sms"})
        if response.user:
            st.success("Phone verification successful! You are now signed in.")
            st.session_state.user = response.user
            st.rerun()
            return response.user
        elif response.error:
            st.error(f"OTP verification failed: {response.error.message}")
            return None
    except Exception as e:
        st.error(f"An unexpected error occurred during OTP verification: {e}")
        return None

# Placeholder for sign-out
def sign_out(supabase: Client):
    """Signs out the current user."""
    try:
        response = supabase.auth.sign_out()
        if response is None: # Supabase sign_out returns None on success or an error
            st.session_state.user = None
            st.success("You have been signed out.")
            st.rerun()
        else: # This case might not be hit if errors are raised as exceptions
             st.error(f"Sign-out failed: {response.error.message if hasattr(response, 'error') and response.error else 'Unknown error'}")
    except Exception as e:
        st.error(f"An unexpected error occurred during sign-out: {e}")

