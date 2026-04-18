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
    data = []
    start = 0

    try:
        while True:
            response = supabase.table(table_name) \
                .select('"date", "type", "duration", "distance", "notes"') \
                .order("date") \
                .range(start, start + page_size - 1) \
                .execute()
            
            # If there is no more data then exit
            if not response.data:
                break
                
            data.extend(response.data)
            
            # If less was returned than requested, this is the last page
            if len(response.data) < page_size:
                break
                
            start += page_size
        
    except Exception as e:
        print(f"Error: {e}")
    
    return data


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
        print(f"|{index+1:^6}|{date:^12}|{type1:^12}|{duration:^10}|{distance:10.2f}|{notes:^24}|")
    sdist = "дистанция"
    print(f"Тринеровок: {len(data)}, {sdist}: {sum:9.1f} км")
    if running_count>0:
        print(f"  {RUNNING}: {running_count}, {sdist}: {running:9.1f} км")
    if walking_count>0:
        print(f"  {WALKING}: {walking_count}, {sdist}: {walking:9.1f} км")
    if cycling_count>0:
        print(f"  {CYCLING}: {cycling_count}, {sdist}: {cycling:9.1f} км")
    if exercise_bike_count>0:
        print(f"  {EXERCISE_BIKE}: {exercise_bike_count}, {sdist}: {exercise_bike:9.1f} км")
    if swimming_count>0:
        print(f"  {SWIMMING}: {swimming_count}, {sdist}: {swimming:9.1f} км")
    if skiing_count>0:
        print(f"  {SKIING}: {skiing_count}, {sdist}: {skiing:9.1f} км")

    print()


def create_year_data(year: int):
    year_data = {
                    "year": year,
                    "run":  0.0,
                    "run_count": 0,
                    "walk": 0.0,
                    "walk_count": 0,
                    "cycl": 0.0,
                    "cycl_count": 0,
                    "exbk": 0.0,
                    "exbk_count": 0,
                    "swim": 0.0,
                    "swim_count": 0,
                    "ski":  0.0,
                    "ski_count": 0,
                }
    return year_data


def find_year_data(year_list, year):
    year_data = None
    for elem in year_list:
        if elem["year"] == year:
            year_data = elem
            break
    if year_data is None: 
        year_data = create_year_data(year)
        year_list.append(year_data)

    return year_data


def add_workout_data(rec, year_data):
    distance = rec["distance"]
    if rec["type"] == RUNNING:
        year_data["run"] += distance
        year_data["run_count"] += 1
    elif rec["type"] == WALKING:
        year_data["walk"] += distance
        year_data["walk_count"] += 1
    elif rec["type"] == CYCLING:
        year_data["cycl"] += distance
        year_data["cycl_count"] += 1
    elif rec["type"] == EXERCISE_BIKE:
        year_data["exbk"] += distance
        year_data["exbk_count"] += 1
    elif rec["type"] == SWIMMING:
        year_data["swim"] += distance
        year_data["swim_count"] += 1
    elif rec["type"] == SKIING:
        year_data["ski"] += distance
        year_data["ski_count"] += 1


def sum_workout_data(summ, year_data):
    summ["run"] += year_data["run"]
    summ["run_count"] += year_data["run_count"]
    summ["walk"] += year_data["walk"]
    summ["walk_count"] += year_data["walk_count"]
    summ["cycl"] +=  year_data["cycl"]
    summ["cycl_count"] += year_data["cycl_count"]
    summ["exbk"] += year_data["exbk"]
    summ["exbk_count"] += year_data["exbk_count"]
    summ["swim"] += year_data["swim"]
    summ["swim_count"] += year_data["swim_count"]
    summ["ski"] += year_data["ski"]
    summ["ski_count"] += year_data["ski_count"]


def counting_all_data_by_year(data):
    year_list = []
    for rec in data:
        year = datetime.fromisoformat(rec['date']).year
        if len(year_list)==0:
            year_data = create_year_data(year)
            year_list.append(year_data)
            add_workout_data(rec, year_data)
        year_data = find_year_data(year_list, year)
        add_workout_data(rec, year_data)
    year_list.sort(key=lambda x: x['year'])
    summ = create_year_data(0)
    dist = 'Дист,км'
    n = 'Кол'
    print('-'*86)
    print(f"|{'Год':^6}|{'Бег':^12}|{'Ходьба':^12}|{'Лыжи':^12}|{'Велосипед':^12}|{'Велотренажер':^12}|{'Плавание':^12}|") 
    print(f"|{'':^6}|{dist:^7}|{n:^4}|{dist:^7}|{n:^4}|{dist:^7}|{n:^4}|{dist:^7}|{n:^4}|{dist:^7}|{n:^4}|{dist:^7}|{n:^4}|") 
    print('-'*86)
    for e in year_list: 
        sum_workout_data(summ, e)
        run = e["run"]
        run_count = e["run_count"]
        walk = e["walk"]
        walk_count = e["walk_count"]
        ski = e["ski"]
        ski_count = e["ski_count"]
        cycl = e["cycl"]
        cycl_count = e["cycl_count"]
        exbk = e["exbk"]
        exbk_count = e["exbk_count"]
        swim = e["swim"]
        swim_count = e["swim_count"]
        runf="7.1f"
        walf="7.1f"
        skif="7.1f"
        cycf="7.1f"
        exbf="7.1f"
        swif="7.1f"
        if run==0:
            run = '-'
            run_count = '-'
            runf="^7"
        if walk==0:
            walk = '-'
            walk_count = '-'
            walf="^7"
        if ski==0:
            ski = '-'
            ski_count = '-'
            skif="^7"
        if cycl==0:
            cycl = '-'
            cycl_count = '-'
            cycf="^7"
        if exbk==0:
            exbk = '-'
            exbk_count = '-'
            exbf="^7"
        if swim==0:
            swim = '-'
            swim_count = '-'
            swif="^7"
        print(f"|{e["year"]:^6}|{run:{runf}}|{run_count:>4}|{walk:{walf}}|{walk_count:>4}|{ski:{skif}}|{ski_count:>4}|"
              f"{cycl:{cycf}}|{cycl_count:>4}|{exbk:{exbf}}|{exbk_count:>4}|{swim:{swif}}|{swim_count:>4}|") 

    print('-'*86)
    run = summ["run"]
    run_count = summ["run_count"]
    walk = summ["walk"]
    walk_count = summ["walk_count"]
    ski = summ["ski"]
    ski_count = summ["ski_count"]
    cycl = summ["cycl"]
    cycl_count = summ["cycl_count"]
    exbk = summ["exbk"]
    exbk_count = summ["exbk_count"]
    swim = summ["swim"]
    swim_count = summ["swim_count"]
    runf="7.1f"
    walf="7.1f"
    skif="7.1f"
    cycf="7.1f"
    exbf="7.1f"
    swif="7.1f"
    if run==0:
        run = '-'
        run_count = '-'
        runf="^7"
    if walk==0:
        walk = '-'
        walk_count = '-'
        walf="^7"
    if ski==0:
        ski = '-'
        ski_count = '-'
        skif="^7"
    if cycl==0:
        cycl = '-'
        cycl_count = '-'
        cycf="^7"
    if exbk==0:
        exbk = '-'
        exbk_count = '-'
        exbf="^7"
    if swim==0:
        swim = '-'
        swim_count = '-'
        swif="^7"
    print(f"|{"Итого":^6}|{run:{runf}}|{run_count:>4}|{walk:{walf}}|{walk_count:>4}|{ski:{skif}}|{ski_count:>4}|"
            f"{cycl:{cycf}}|{cycl_count:>4}|{exbk:{exbf}}|{exbk_count:>4}|{swim:{swif}}|{swim_count:>4}|") 
    print(f"Всего тренировок: {len(data)}")
    print()


def main():
    print("Hello from fittrack!")
    while True:
        code = input("Введите 1-диапазон лет; 2-данные за год; 3-суммы по годам; 4-добавить: ")
        
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
            year = int(input("Введите год: "))

            try:
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
                supabase = connect_to_db()

                response = supabase.table('workouts')\
                .select('date,type,duration,distance,notes')\
                .gte('date', start_date)\
                .lte('date', end_date)\
                .order("date") \
                .execute()
    
                # Verification and output of results
                if response.data:
                    print(f"Найдено записей за {year}: {len(response.data)}")
                    out_data(response.data)
                else:
                    print(f"Нет записей за {year}")
        
            except Exception as e:
                print(f"Ошибка: {e}")

        elif code=="3":
            supabase = connect_to_db()
            data = fetch_all_rows(supabase, "workouts")
            if data:
                counting_all_data_by_year(data)
        elif code=="4":
            try:
                typew = ""
                dt = input("Введите дату 'ГГГГ-ММ-ДД':")
                tp = input(f"Введите тип {RUNNING}-1, {WALKING}-2, {CYCLING}-3, {EXERCISE_BIKE}-4, {SWIMMING}-5, {SKIING}-6: ")
                ds = float(input("Введите дистанцию, км: "))
                dr = float(input("Длительность, мин: "))
                nt = input("Примечание: ")
                if tp=='1':
                    typew = RUNNING
                if tp=='2':
                    typew = WALKING
                if tp=='3':
                    typew = CYCLING
                if tp=='4':
                    typew = EXERCISE_BIKE
                if tp=='5':
                    typew = SWIMMING
                if tp=='6':
                    typew = SKIING

                supabase = connect_to_db()
                user_id = supabase.auth.get_user().user.id
                rec = {
                    "user_id": user_id, 
                    "date": dt,
                    "type": typew,
                    "distance": ds,
                    "duration": dr,
                    "notes": nt
                }
                response = supabase.table("workouts").insert(rec).execute()
                print(f"\n✅ Успешно добавлено! ID записи: {response.data[0]['id']}")
            except ValueError:
                print("\n❌ Ошибка: Дистанция и время должны быть числами (через точку).")
            except Exception as e:
                print(f"\n❌ Ошибка базы данных: {e}")
        else:
            print("Выход")
            break


if __name__ == "__main__":

    main()
