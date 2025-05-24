from django.http import HttpResponse
import requests
import datetime
from django.shortcuts import redirect, render


def index(request):
    api_url = 'https://api09.horseracing.software/bha/v1/racecourses'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer 1|LuWZoUL0sMuGBvKboxSGTmYbhiZ9LwSpzBKP8mCQ',
        'Origin': 'https://www.britishhorseracing.com',
        'Referer': 'https://www.britishhorseracing.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    races = {}
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        sorted_data = sorted(
            data['data'],
            key=lambda x: datetime.datetime.strptime(x['nextFixtureDate'], "%Y-%m-%d") if x['nextFixtureDate'] else datetime.datetime.max
        )
        
        races = {
            "success": data["success"],
            "total": data["total"],
            "data": sorted_data
        }

    except requests.RequestException as e:
        print("Error fetching data from API:", e)

    return render(request, "horseapp/index.html", {'races': races})

def fixture_detail(request, year, fixture_id, course_name):
    api_url = f'https://api09.horseracing.software/bha/v1/fixtures/{year}/{fixture_id}/races'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer 1|LuWZoUL0sMuGBvKboxSGTmYbhiZ9LwSpzBKP8mCQ',
        'Origin': 'https://www.britishhorseracing.com',
        'Referer': 'https://www.britishhorseracing.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    races = []
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        races = data['data']
    except requests.RequestException as e:
        print("Error fetching fixture races:", e)

    return render(request, 'horseapp/fixture_detail.html', {
        'races': races,
        'fixture_id': fixture_id,
        'year': year,
        'course_name': course_name
    })


def find_fixture_reverse(course_id, fixture_date_str):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer 1|LuWZoUL0sMuGBvKboxSGTmYbhiZ9LwSpzBKP8mCQ',
        'Origin': 'https://www.britishhorseracing.com',
        'User-Agent': 'Mozilla/5.0',
    }
    print(course_id)
    try:
        first = requests.get(f"https://api09.horseracing.software/bha/v1/fixtures?courseId={course_id}", headers=headers)
        first.raise_for_status()
        total_pages = first.json().get("last_page", 1)
    except requests.RequestException as e:
        print("⚠️ Could not get total pages:", e)
        return None

    for page in range(total_pages, 0, -1):
        try:
            url = f"https://api09.horseracing.software/bha/v1/fixtures?page={page}&courseId={course_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            fixtures = response.json().get("data", [])

            for fixture in fixtures:
                if fixture["fixtureDate"] == fixture_date_str:
                    return fixture
        except requests.RequestException as e:
            print(f"Error on page {page}:", e)

    return None

def racecourse_redirect_to_fixture(request, course_id, fixture_date, course_name):
    fixture = find_fixture_reverse(course_id, fixture_date)
    
    if fixture:
        year = fixture["fixtureDate"][:4]
        fixture_id = fixture["fixtureId"]
        return redirect('fixture_detail', year=year, fixture_id=fixture_id, course_name=course_name)
    else:
        return HttpResponse("No matching fixture found.", status=404)
    
def race_detail(request, year, race_id, race_name):
    url = f"https://api09.horseracing.software/bha/v1/races/{year}/{race_id}/0/entries"
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer 1|LuWZoUL0sMuGBvKboxSGTmYbhiZ9LwSpzBKP8mCQ',
        'Origin': 'https://www.britishhorseracing.com',
        'User-Agent': 'Mozilla/5.0',
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        runners = response.json().get("data", [])
    except requests.RequestException as e:
        print(f"Error fetching race detail: {e}")
        return HttpResponse("Unable to fetch race details.", status=500)

    for r in runners:
        horse_stats_list = get_horse_stats(r["animalId"])
        
        if horse_stats_list and len(horse_stats_list) > 0:
            horse_stats_data = horse_stats_list[0]
            
            total_runs = horse_stats_data.get("totalRuns", 0)
            total_wins = horse_stats_data.get("totalWins", 0)
            total_places = horse_stats_data.get("totalPlaces", 0)

            if total_runs > 0:
                win_pct = (total_wins / total_runs) * 100
                place_pct = (total_places / total_runs) * 100
            else:
                win_pct = 0.0
                place_pct = 0.0

            horse_stats_data['win_pct'] = round(win_pct, 2)
            horse_stats_data['place_pct'] = round(place_pct, 2)

            r["horse_stats"] = horse_stats_data
        else:
            r["horse_stats"] = None

    return render(request, "horseapp/race_detail.html", {
        "runners": runners,
        "race_id": race_id,
        "year": year,
        "race_name": race_name
    })

def get_horse_stats(animal_id):
    import requests
    
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer 1|LuWZoUL0sMuGBvKboxSGTmYbhiZ9LwSpzBKP8mCQ',
        'Origin': 'https://www.britishhorseracing.com',
        'User-Agent': 'Mozilla/5.0',
    }

    url = f"https://api09.horseracing.software/bha/v1/racehorses/{animal_id}"
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        rawdata = res.json()
        data = rawdata["data"]
        runs = data["performanceDetails"]
    except requests.RequestException as e:
        print(f"Error fetching horse {animal_id} performance:", e)
        
    return runs
