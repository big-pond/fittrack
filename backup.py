import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json
import argparse
from pathlib import Path

# Load variables from file .env to environment
def read_database(all_data):
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    password: str = os.environ.get("USER_PASSWORD")

    supabase: Client = create_client(url, key)
    # 1. Logging in (the user's token is saved in the client automatically)
    supabase.auth.sign_in_with_password({"email": "py99@mail.ru", "password": password})

    start = 0
    page_size = 100

    try:
        while True:
            response = supabase.table("workouts") \
                .select("*") \
                .range(start, start + page_size - 1) \
                .execute()
            
            # If there is no more data then exit
            if not response.data:
                break

            all_data.extend(response.data)
            
            # If less was returned than requested, this is the last page
            if len(response.data) < page_size:
                break
                
            start += page_size
    

    except Exception as e:
        print(f"Error: {e}")

def format_value(v):
    if v is None: return "NULL"
    if isinstance(v, (int, float)): return str(v)
    # SQL standard: escaping a single quote by doubling it
    return f"'{str(v).replace("'", "''")}'"



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Backup my workout database',
        usage='%(prog)s [options] filename'
    )
    
    parser.add_argument('filename',
                        help='Backup file name with directory')
    
    parser.add_argument('-t', '--type', 
                        default='sql',
                        help='Type of backup file: json or sql')
    
    args = parser.parse_args()
    
    filepath = Path(args.filename).expanduser().resolve()
    filetype = args.type.lower()

    if filepath.parent.is_dir():
        all_data = []
        if filetype=='sql':
            read_database(all_data);
            try:
                record_count = len(all_data)
                table = "workouts"
                # Take the column names from the first dictionary
                cols = ",".join(f'"{k}"' for k in all_data[0].keys())
                # Collecting all strings with values in parentheses
                values_list = []
                for item in all_data:
                    row = ",".join(format_value(v) for v in item.values())
                    values_list.append(f"({row})")
                # Combining everything into one command
                sql_final = f'INSER INTO "{table}" ({cols}) VALUES\n' + ",\n".join(values_list)
                # Writing  to a file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(sql_final)
                print(f"Record count: {record_count}")
            except Exception as e:
                print(f"Error: {e}")

        elif filetype=='json':
            read_database(all_data);
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            print(f"Record count: {len(all_data)}")
        else:
            print(" Unsupported file type")
