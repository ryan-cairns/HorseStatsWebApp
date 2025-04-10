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
        
        # Sort by nextFixtureDate (if it exists and is not None)
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

def fixture_detail(request, year, fixture_id):
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
        'year': year
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
        print("Total pages:", total_pages)
    except requests.RequestException as e:
        print("⚠️ Could not get total pages:", e)
        return None

    for page in range(total_pages, 0, -1):
        print(page)
        try:
            url = f"https://api09.horseracing.software/bha/v1/fixtures?page={page}&courseId={course_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            fixtures = response.json().get("data", [])

            for fixture in fixtures:
                print(fixture_date_str)
                print(fixture["fixtureDate"])
                if fixture["fixtureDate"] == fixture_date_str:
                    return fixture
        except requests.RequestException as e:
            print(f"Error on page {page}:", e)

    return None

def racecourse_redirect_to_fixture(request, course_id, fixture_date):
    fixture = find_fixture_reverse(course_id, fixture_date)
    
    if fixture:
        year = fixture["fixtureDate"][:4]
        fixture_id = fixture["fixtureId"]
        return redirect('fixture_detail', year=year, fixture_id=fixture_id)
    else:
        return HttpResponse("No matching fixture found.", status=404)