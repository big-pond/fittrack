import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load variables from file .env to environment
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
password: str = os.environ.get("USER_PASSWORD")

supabase: Client = create_client(url, key)

# 1. Logging in (the user's token is saved in the client automatically)
supabase.auth.sign_in_with_password({"email": "py99@mail.ru", "password": password})

def fetch_all_rows(table_name, page_size=100):
    all_data = []
    start = 0

    while True:
        response = supabase.table(table_name) \
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
    
    return all_data


def out_data(data):
    for index, rec in enumerate(data):
        date = rec["date"]
        type1 = rec["type"]
        duration = rec["duration"]
        distance = rec["distance"]
        notes = rec["notes"]
        print(f"{index}, {date}, {type1}, {duration}, {distance}, {notes}") 
    print()


def main():
    print("Hello from fittrack!")
    while True:
        code = input("Input 1-all data; 2-year: ")
        if code=="1":
            try:
                all_record = fetch_all_rows("workouts")
                for record in all_record:
                    print(record)
                print(f"Записей: {len(all_record)}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif code=="2":
            year = int(input("Input year: "))

            try:
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
    
                response = supabase.table('workouts')\
                .select('date,type,duration,distance,notes')\
                .gte('date', start_date)\
                .lte('date', end_date)\
                .execute()
    
                # Verification and output of results
                if response.data:
                    print(f"Найдено записей за {year}: {len(response.data)}")
                    out_data(response.data)
                else:
                    print(f"Нет записей за {year}")
        
            except Exception as e:
                print(f"Ошибка: {e}")

        else:
            print("Exit")
            break


if __name__ == "__main__":
    main()
