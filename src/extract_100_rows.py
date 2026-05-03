import csv
import os

def main():
    input_file = "data/processed/games_detailed_info2025.csv"
    output_file = "data/processed/games_detailed_info2025_100_rows.csv"
    
    print(f"Reading from {input_file}...")
    
    with open(input_file, 'r', newline='', encoding='utf-8') as f_in, \
         open(output_file, 'w', newline='', encoding='utf-8') as f_out:
        
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        # Write header
        header = next(reader)
        writer.writerow(header)
        
        # Write exactly 100 rows
        count = 0
        for row in reader:
            writer.writerow(row)
            count += 1
            if count >= 100:
                break
                
    print(f"Successfully extracted {count} rows to {output_file}")

if __name__ == "__main__":
    main()
