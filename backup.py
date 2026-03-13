import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load variables from file .env to environment
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
password: str = os.environ.get("USER_PASSWORD")

# print(f"{url} {key}")
# print(password)

supabase: Client = create_client(url, key)
# 1. Logging in (the user's token is saved in the client automatically)
supabase.auth.sign_in_with_password({"email": "py99@mail.ru", "password": password})

all_data = []
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
    
    for record in all_data:
        print(record)
    print(f"Записей: {len(all_data)}")

except Exception as e:
    print(f"Ошибка: {e}")


