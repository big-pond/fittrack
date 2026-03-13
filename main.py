import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load variables from file .env to environment
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
password: str = os.environ.get("USER_PASSWORD")

supabase: Client = create_client(url, key)

# 1. Logging in (the user's token is saved in the client automatically)
supabase.auth.sign_in_with_password({"email": "py99@mail.ru", "password": password})

def main():
    print("Hello from fittrack!")
    while True:
        code = input("Input 1-all data; 2-test: ")
        if code=="1":
            response = supabase.table("workouts").select("date,type,duration,distance,notes").execute()
            data = response.data
            for index, rec in enumerate(data):
                date = rec["date"]
                type1 = rec["type"]
                duration = rec["duration"]
                distance = rec["distance"]
                notes = rec["notes"]
                print(f"{index}, {date}, {type1}, {duration}, {distance}, {notes}") 
        elif code=="2":
            print("code =", code)
        else:
            print("code =", code, "exit")
            break


if __name__ == "__main__":
    main()
