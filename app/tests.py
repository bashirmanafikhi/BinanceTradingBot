import csv
import os
import pandas as pd

def split_and_save_data(data_dir='app\\bitcoin_historical_data\\2019-2023', file_name='candlesticks-S.csv', interval_months=3):
    try:
        file_path = os.path.join(data_dir, file_name)

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Read the header

            data = []
            current_chunk_start_date = None
            current_chunk_end_date = None

            for row in reader:
                # Skip rows where the value in the third column is 'NaN'
                if row[2] == 'NaN':
                    continue
                timestamp = pd.to_datetime(row[0], unit='ms')

                if current_chunk_start_date is None:
                    current_chunk_start_date = timestamp

                if current_chunk_end_date is None or timestamp <= current_chunk_end_date:
                    data.append(row)
                else:
                    save_chunk_to_file(data, header, current_chunk_start_date, current_chunk_end_date, data_dir)
                    data = [row]
                    current_chunk_start_date = timestamp

                current_chunk_end_date = current_chunk_start_date + pd.DateOffset(months=interval_months)

            # Save the last chunk
            save_chunk_to_file(data, header, current_chunk_start_date, current_chunk_end_date, data_dir)

    except Exception as e:
        print(f"Error splitting and saving data: {e}")

def save_chunk_to_file(data, header, start_date, end_date, data_dir):
    chunk_data = pd.DataFrame(data, columns=header)
    chunk_data["date"] = pd.to_datetime(chunk_data["timestamp"], unit='ms')
    chunk_data = chunk_data.iloc[::-1]

    output_file_name = f"chunk_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
    output_file_path = os.path.join(data_dir, output_file_name)

    chunk_data.to_csv(output_file_path, index=False)
    print(f"Chunk data ({start_date} to {end_date}) saved to {output_file_path}")



# Example usage
split_and_save_data()
