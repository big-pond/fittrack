import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
from pathlib import Path

RUNNING = 'бег'
WALKING = 'ходьба'
CYCLING = 'велосипед' 
EXERCISE_BIKE = 'велотренажер' 
SWIMMING = 'плавание' 
SKIING = 'лыжи'

def connect_to_db():
    # Load variables from file .env to environment
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    password: str = os.environ.get("USER_PASSWORD")

    supabase: Client = create_client(url, key)

    # 1. Logging in (the user's token is saved in the client automatically)
    supabase.auth.sign_in_with_password({"email": "py99@mail.ru", "password": password})

    return supabase


def min_to_hms(minutes):
    mn = float(minutes)
    h= int(mn//60)
    m = int(mn - h*60)
    s = int(round((mn - h*60 - m)*60))
    return f'{h:02}:{m:02}:{s:02}'

def fetch_all_rows(supabase, table_name, page_size=100):
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
    sum = 0.0
    running =  walking =  cycling = exercise_bike = swimming = skiing = 0.0
    running_count =  walking_count =  cycling_count = exercise_bike_count = swimming_count = skiing_count = 0
    print("-" * 81)
    print(f"|{'N пп':^6}|{'Дата':^12}|{'Тип':^12}|{'Время, мин':^10}|{'Дистанция':^10}|{'Примечание':^24}|") 
    print("-" * 81)
    for index, rec in enumerate(data):
        date = rec["date"]
        type1 = rec["type"]
        duration = rec["duration"]
        distance = rec["distance"]
        notes = rec["notes"]
        if type1==RUNNING:
            running += distance
            running_count += 1
        elif type1==WALKING:
            walking += distance 
            walking_count += 1
        elif type1==CYCLING:
            cycling += distance 
            cycling_count += 1
        elif type1==EXERCISE_BIKE:
            exercise_bike += distance 
            exercise_bike_count += 1
        elif type1==SWIMMING:
            swimming += distance 
            swimming_count += 1
        elif type1==SKIING:
            skiing += distance 
            skiing_count += 1
        sum += distance
        if duration:
            duration = min_to_hms(duration)
        else:
            duration = "-"
        if notes==None:
            notes = "-"
        print(f"|{index:^6}|{date:^12}|{type1:^12}|{duration:^10}|{distance:10.2f}|{notes:^24}|")
    print(f"Тринеровок: {len(data)}, дистанция: {sum:9.1f} км")
    if running_count>0:
        print(f"  {RUNNING}: {running_count}, дистанция: {running:9.1f} км")
    if walking_count>0:
        print(f"  {WALKING}: {walking_count}, дистанция: {walking:9.1f} км")
    if cycling_count>0:
        print(f"  {CYCLING}: {cycling_count}, дистанция: {cycling:9.1f} км")
    if exercise_bike_count>0:
        print(f"  {EXERCISE_BIKE}: {exercise_bike_count}, дистанция: {exercise_bike:9.1f} км")
    if swimming_count>0:
        print(f"  {SWIMMING}: {swimming_count}, дистанция: {swimming:9.1f} км")
    if skiing_count>0:
        print(f"  {SKIING}: {skiing_count}, дистанция: {skiing:9.1f} км")

    print()


def main():
    print("Hello from fittrack!")
    while True:
        code = input("Input 1-amounts by year; 2-data for the year: ")
        
        if code=="1":
            supabase = connect_to_db()
            # Получаем минимальную дату
            min_res = supabase.table("workouts") \
                .select("date") \
                .order("date", desc=False) \
                .limit(1) \
                .single() \
                .execute()

            # Получаем максимальную дату
            max_res = supabase.table("workouts") \
                .select("date") \
                .order("date", desc=True) \
                .limit(1) \
                .single() \
                .execute()

            # Извлекаем год с помощью datetime
            min_year = datetime.fromisoformat(min_res.data['date']).year
            max_year = datetime.fromisoformat(max_res.data['date']).year

            print(f"Диапазон лет: {min_year} - {max_year}")
        elif code=="2":
            year = int(input("Input year: "))

            try:
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
                supabase = connect_to_db()

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
