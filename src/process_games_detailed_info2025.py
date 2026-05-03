import csv
import os

def process_csv(input_path, output_path, limit=None):
    """
    Processes the raw BGG CSV to extract and rename specific columns.
    If limit is set, stops after processing 'limit' data rows.
    """
    target_columns = [
        "id",
        "name",
        "description",
        "boardgamecategory",
        "boardgamemechanic",
        "boardgamedesigner",
        "usersrated",
        "rating",
        "bayes_rating",
        "num_comments",
        "playtime",
        "min_playtime",
        "max_playtime"
    ]

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, 'r', newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
         
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=target_columns)
        
        writer.writeheader()
        
        count = 0
        for row in reader:
            if limit is not None and count >= limit:
                break
            count += 1
            processed_row = {
                "id": row.get("id"),
                "name": row.get("name"),
                "description": row.get("description"),
                "boardgamecategory": row.get("boardgamecategory"),
                "boardgamemechanic": row.get("boardgamemechanic"),
                "boardgamedesigner": row.get("boardgamedesigner"),
                "usersrated": row.get("usersrated"),
                "rating": row.get("average"),
                "bayes_rating": row.get("bayesaverage"),
                "num_comments": row.get("numcomments"),
                "playtime": row.get("playingtime"),
                "min_playtime": row.get("minplaytime"),
                "max_playtime": row.get("maxplaytime")
            }
            writer.writerow(processed_row)

def main():
    input_file = "data/raw/games_detailed_info2025.csv"
    output_file = "data/processed/games_detailed_info2025.csv"
    
    # Optional: allow relative execution from either root or src dir
    # we'll resolve relative paths strictly assuming we run from root.
    
    print(f"Processing data from {input_file}...")
    process_csv(input_file, output_file)
    print(f"Data successfully processed and saved to {output_file}.")

    output_file_100 = "data/processed/games_detailed_info2025_100_rows.csv"
    print(f"Processing 100-row sample from {input_file}...")
    process_csv(input_file, output_file_100, limit=100)
    print(f"100-row sample successfully processed and saved to {output_file_100}.")

if __name__ == "__main__":
    main()
