import pandas as pd
import os

def main():
    # Input file
    input_file = 'data/weblog.csv'
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return
    
    print(f"Processing CSV file: {input_file}")
    
    # Read CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Read {len(df)} log entries")
        print(f"Columns: {df.columns.tolist()}")
        
        # Print sample to understand structure
        print("\nSample data (first 3 rows):")
        print(df.head(3))
        
        # Now process based on the structure of the file
        # We'll need to map the existing columns to our expected structure:
        # - timestamp
        # - level (INFO, WARN, ERROR)
        # - service
        # - message
        # - metadata (dictionary with additional info)
        
        # Determine if we need to create new columns or rename existing ones
        # This is a placeholder - you'll need to adjust based on your actual CSV structure
        processed_df = pd.DataFrame()
        
        # Map existing timestamp column or create one
        if 'timestamp' in df.columns:
            processed_df['timestamp'] = df['timestamp']
        elif 'date' in df.columns:
            processed_df['timestamp'] = df['date']
        else:
            # Use first available datetime column or create a default
            processed_df['timestamp'] = "2023-01-01T00:00:00"  # Default timestamp
        
        # Add log level (based on HTTP status code if available)
        if 'status' in df.columns:
            def determine_level(status):
                try:
                    status = int(status)
                    if status < 400:
                        return 'INFO'
                    elif status < 500:
                        return 'WARN'
                    else:
                        return 'ERROR'
                except:
                    return 'INFO'  # Default level
            
            processed_df['level'] = df['status'].apply(determine_level)
        else:
            processed_df['level'] = 'INFO'  # Default level
        
        # Add service field
        processed_df['service'] = 'web-server'
        
        # Add meaningful message
        if 'status' in df.columns and 'request' in df.columns:
            def create_message(row):
                status_messages = {
                    200: 'Request successful',
                    201: 'Resource created',
                    301: 'Resource moved permanently',
                    302: 'Resource moved temporarily',
                    304: 'Not modified',
                    400: 'Bad request',
                    401: 'Unauthorized',
                    403: 'Forbidden',
                    404: 'Resource not found',
                    500: 'Internal server error',
                    502: 'Bad gateway',
                    503: 'Service unavailable'
                }
                
                try:
                    status = int(row['status'])
                    path = row['request']
                    
                    message = status_messages.get(status, f'Status code: {status}')
                    return f"{message} for {path}"
                except:
                    return "Web server log entry"
            
            processed_df['message'] = df.apply(create_message, axis=1)
        else:
            # Create a default message
            processed_df['message'] = "Web server log entry"
        
        # Create metadata with all remaining columns
        def create_metadata(row):
            metadata = {}
            for col in df.columns:
                if col not in ['timestamp', 'level', 'service', 'message']:
                    metadata[col] = row[col]
            return metadata
        
        processed_df['metadata'] = df.apply(create_metadata, axis=1)
        
        # Save as CSV for easier processing
        output_file = "data/processed_web_logs.csv"
        processed_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully converted to CSV: {output_file}")
        print(f"Final structure: {processed_df.columns.tolist()}")
        print("\nSample processed data (first 3 rows):")
        print(processed_df[['timestamp', 'level', 'service', 'message']].head(3))
        
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    main()