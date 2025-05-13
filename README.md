# Excel Enrichment Streamlit Application

This Streamlit web application allows users to upload an Excel (.xlsx) file, process it using a predefined ETL (Extract, Transform, Load) logic to append a new "Group" sheet, and then download the enriched workbook.

## Features

*   **User Authentication**: Secure login via email and password or New Zealand mobile number (SMS OTP) using Supabase.
*   **File Upload**: Users can upload Excel files with the `.xlsx` extension.
*   **ETL Processing**: The application integrates a Python script (`etl.py`) to perform data aggregation and append a "Group" sheet. This sheet summarises Profit & Loss data from specific sheets within the uploaded workbook (TTW, MRP, TPO, WFA, PTC).
*   **Customisable Prorating**: Users can specify the number of months (Year-to-Date) for prorating annual budget figures during the ETL process.
*   **File Download**: After processing, users can download the enriched Excel workbook, which includes all original sheets plus the newly added "Group" sheet.
*   **UK Spelling**: The application and its documentation use UK English spelling.

## Project Structure

```
streamlit_app/
├── .streamlit/
│   ├── config.toml       # Streamlit configuration (if needed)
│   └── secrets.toml      # Supabase credentials (MUST BE CREATED BY USER)
├── data/                 # (Optional) For sample data or persistent storage if extended
├── utils/
│   └── auth.py           # Supabase authentication helper functions
├── app.py                # Main Streamlit application script
├── etl.py                # Python script for ETL logic (appending Group sheet)
├── requirements.txt      # Python package dependencies
├── todo.md               # Project task checklist
└── README.md             # This file
```

## Setup and Configuration

1.  **Clone the Repository (if applicable)**:
    ```bash
    # git clone <repository_url>
    # cd streamlit_app_directory
    ```

2.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Supabase Credentials**:
    You **must** create a `secrets.toml` file in the `.streamlit` directory within your project (`streamlit_app/.streamlit/secrets.toml`).
    Add your Supabase project URL and anon key to this file as follows:

    ```toml
    [connections.supabase]
    SUPABASE_URL = "your_actual_supabase_url"
    SUPABASE_KEY = "your_actual_supabase_anon_key"
    ```
    Replace `"your_actual_supabase_url"` and `"your_actual_supabase_anon_key"` with the credentials from your Supabase project settings (API section).

    **Important**: Ensure your Supabase project has Email and Phone (SMS) authentication enabled. For SMS OTP, you will also need to configure an SMS provider (e.g., Twilio) within your Supabase project settings.

## Running the Application

Once the setup is complete, you can run the Streamlit application using the following command from the root directory of the project (`streamlit_app/`):

```bash
streamlit run app.py
```

The application should open in your web browser.

## Usage

1.  **Login/Sign Up**:
    *   Use the sidebar to either log in with your existing credentials or sign up for a new account.
    *   You can choose between email/password authentication or login via a New Zealand mobile number (which will send an SMS OTP).
2.  **Upload File**:
    *   Once logged in, the main area of the application will display a file uploader.
    *   Click "Browse files" to select an `.xlsx` file from your computer.
    *   The Excel file should contain sheets named TTW, MRP, TPO, WFA, and PTC for the ETL process to work correctly.
3.  **Set Prorating Months**:
    *   Adjust the "Number of months YTD for prorating annual budgets" input (default is 9) as required for your financial data.
4.  **Process File**:
    *   Click the "Process File" button.
    *   The application will call the `append_group_sheet` function from `etl.py` to process your uploaded file.
5.  **Download Enriched Workbook**:
    *   If the processing is successful, a download button will appear.
    *   Click "Download Enriched Workbook (.xlsx)" to save the modified file to your computer. The downloaded file will have `_enriched` appended to its original name.

## ETL Logic (`etl.py`)

The `append_group_sheet` function in `etl.py` performs the following steps:

1.  Reads the input Excel file (provided as bytes).
2.  Loads data from predefined sheets: TTW, MRP, TPO, WFA, PTC.
3.  Prorates any 'AnnualBudget' columns in these sheets based on the number of months specified by the user.
4.  Creates a master list of all unique categories found across these sheets.
5.  Aggregates 'Actual' and 'ProratedBudget' figures into clusters:
    *   TTW+MRP Actuals & Budget
    *   TPO Actuals & Budget
    *   WFA+PTC Actuals & Budget
6.  Creates a new sheet named "Group" containing these aggregated figures.
7.  Returns the entire workbook (original sheets + new "Group" sheet) as bytes.

## Dependencies

*   `streamlit`: For creating the web application interface.
*   `pandas`: For data manipulation and Excel file handling.
*   `openpyxl`: As the engine for pandas to read/write `.xlsx` files.
*   `supabase`: For interacting with Supabase for authentication.

These are listed in `requirements.txt`.

