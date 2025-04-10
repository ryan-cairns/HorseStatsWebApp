import requests
import datetime
from django.shortcuts import render


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
