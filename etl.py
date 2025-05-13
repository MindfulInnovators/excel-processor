# ETL Logic (UK Spelling)
import pandas as pd
import io

def append_group_sheet(input_bytes: bytes, months: int = 9):
    """Appends a 'Group' sheet aggregating P&L data from multiple sheets.

    Args:
        input_bytes: Bytes of the input Excel file containing TTW, MRP, TPO, WFA, PTC sheets.
        months: Number of months YTD for prorating annual budgets (default: 9).

    Returns:
        Bytes of the output Excel file with the new Group sheet, or None if an error occurs.
    """
    try:
        # Configuration for each P&L sheet
        SHEETS = {
            'TTW': {'cat': 'Category', 'actual': 'Actual', 'budget': 'AnnualBudget'},
            'MRP': {'cat': 'Category', 'actual': 'Actual', 'budget': 'AnnualBudget'},
            'TPO': {'cat': 'Category', 'actual': 'Actual', 'budget': 'AnnualBudget'},
            'WFA': {'cat': 'Category', 'actual': 'Actual', 'budget': 'AnnualBudget'},
            'PTC': {'cat': 'Category', 'actual': 'Actual', 'budget': 'AnnualBudget'},
        }

        # Step 1: Load sheets into DataFrames from input_bytes
        xls = pd.ExcelFile(input_bytes)
        sheet_names_in_file = xls.sheet_names
        
        # Check if all required sheets are present
        required_sheets = list(SHEETS.keys())
        missing_sheets = [sheet for sheet in required_sheets if sheet not in sheet_names_in_file]
        if missing_sheets:
            # Consider how to report this error back to the Streamlit app
            # For now, let's print and return None, Streamlit app should handle this
            print(f"Error: Missing required sheets: {', '.join(missing_sheets)}")
            return None

        dfs = {}
        for name, cfg in SHEETS.items():
            df = pd.read_excel(xls, sheet_name=name)
            # Prorate the annual budget into months YTD
            if cfg['budget'] in df.columns:
                # Ensure budget column is numeric, coercing errors to NaN, then fill NaN with 0
                df[cfg['budget']] = pd.to_numeric(df[cfg['budget']], errors='coerce').fillna(0)
                df['ProratedBudget'] = df[cfg['budget']] / 12 * months
            else:
                df['ProratedBudget'] = 0.0
            
            # Ensure actual column is numeric
            if cfg['actual'] in df.columns:
                df[cfg['actual']] = pd.to_numeric(df[cfg['actual']], errors='coerce').fillna(0)
            else:
                df[cfg['actual']] = 0.0 # Add actual column with 0 if missing

            dfs[name] = df

        # Step 2: Build master category list
        all_cats = pd.Index([])
        for name, cfg in SHEETS.items():
            if cfg['cat'] in dfs[name].columns:
                all_cats = all_cats.union(pd.Index(dfs[name][cfg['cat']].astype(str).unique())) # Ensure categories are strings and unique
            else:
                # Handle missing category column, perhaps log a warning or error
                print(f"Warning: Category column '{cfg['cat']}' not found in sheet '{name}'.")
        
        all_cats = all_cats.sort_values()
        group = pd.DataFrame({'Category': all_cats})

        # Helper to sum columns across sheets
        def sum_for(sheet_names, column_to_sum):
            series = pd.Series(0.0, index=all_cats, dtype='float64') # Ensure float64 for sums
            for nm in sheet_names:
                cfg = SHEETS[nm]
                # Ensure the category column exists before grouping
                if cfg['cat'] in dfs[nm].columns and column_to_sum in dfs[nm].columns:
                    # Convert category to string for consistent grouping
                    mapped = dfs[nm].astype({cfg['cat']: str}).groupby(cfg['cat'])[column_to_sum].sum()
                    series = series.add(mapped, fill_value=0)
                else:
                    print(f"Warning: Column '{cfg['cat']}' or '{column_to_sum}' not found in sheet '{nm}' for summing.")
            return series

        # Step 3: Aggregate clusters
        group['TTW+MRP Actuals'] = sum_for(['TTW', 'MRP'], 'Actual')
        group['TTW+MRP Budget'] = sum_for(['TTW', 'MRP'], 'ProratedBudget')
        group['TPO Actuals'] = sum_for(['TPO'], 'Actual')
        group['TPO Budget'] = sum_for(['TPO'], 'ProratedBudget')
        group['WFA+PTC Actuals'] = sum_for(['WFA', 'PTC'], 'Actual')
        group['WFA+PTC Budget'] = sum_for(['WFA', 'PTC'], 'ProratedBudget')

        # Step 4: Write out the updated workbook to bytes
        output_bytes_io = io.BytesIO()
        with pd.ExcelWriter(output_bytes_io, engine='openpyxl') as writer:
            # Write original sheets back
            for sheet_name in sheet_names_in_file:
                original_df = pd.read_excel(xls, sheet_name=sheet_name)
                original_df.to_excel(writer, sheet_name=sheet_name, index=False)
            # Write the new Group sheet
            group.to_excel(writer, sheet_name='Group', index=False)
        
        output_bytes_io.seek(0) # Reset stream position
        return output_bytes_io.getvalue()

    except Exception as e:
        print(f"Error in append_group_sheet: {e}")
        # In a real app, you might want to log this error more formally
        return None

# Original main function for command-line use (optional, can be removed if not needed)
# def main():
#     parser = argparse.ArgumentParser(
#         description="Append a 'Group' sheet aggregating P&L data from multiple sheets."
#     )
#     parser.add_argument(
#         '--input', required=True,
#         help='Path to the input Excel file containing TTW, MRP, TPO, WFA, PTC sheets'
#     )
#     parser.add_argument(
#         '--output', required=True,
#         help='Path for the output Excel file with the new Group sheet'
#     )
#     parser.add_argument(
#         '--months', type=int, default=9,
#         help='Number of months YTD for prorating annual budgets (default: 9)'
#     )
#     args = parser.parse_args()

#     with open(args.input, 'rb') as f:
#         input_bytes_content = f.read()
    
#     processed_bytes = append_group_sheet(input_bytes_content, args.months)

#     if processed_bytes:
#         with open(args.output, 'wb') as f_out:
#             f_out.write(processed_bytes)
#         print(f"Updated Group sheet written to {args.output}")
#     else:
#         print("Failed to process the Excel file.")

# if __name__ == '__main__':
#     main()

