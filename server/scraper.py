import json

import redis
import requests
import pandas
import numpy as np
import logging
from datetime import datetime

logging.basicConfig(format='[%(levelname)s] %(message)s', datefmt='%H:%M:%S', level="INFO")
logger = logging.getLogger()
r = redis.Redis(host='localhost', port=6379, db=0)


class Api:

    def request(self, url: str, params=(), headers=None, auth=None, proxy=None, text=True, *argv):
        """Performs a single request to given url"""
        try:
            client_container = requests.request("GET",
                                                url=url,
                                                headers=headers,
                                                timeout=5
                                                )
            logger.info(msg=f"[{client_container.status_code}, url: {url}")
        except Exception as e:
            logger.info(msg=f"error is {e}")
            return ""
        if text:
            html_content = client_container.text
        else:
            html_content = client_container

        status_code = client_container.status_code
        if status_code != 200:
            logger.info(f"status code is not 200 -> {status_code}; {url}, {proxy}")
            return ""
        return html_content


class LiveScoresParser:
    def __init__(self, sport_name):
        self.api = Api()
        self.sports_keys_map= {
            "soccer": "1",
            "basketball": "2",
            "baseball": "3",
            "ice hockey": "4",
            "tennis": "5",
            "hand ball": "6",
            "floorball": "7",
            "trotting": "8",
            "golf": "9",
            "boxing": "10",
            "motorsport": "11",
            "rugby": "12",
            "aussie rules": "13",  # australian football
            "winter sports": "14",
            "bandy": "15",
            "american football": "16",
            "cycling": "17",
            "specials": "18",
            "snooker": "19",
            "table tennis": "20",
            "cricket": "21",
            "darts": "22",
            "volleyball": "23",
            "field hockey": "24",
        }
        self.sport_name = sport_name
        self.sport_id = self.sports_keys_map.get(self.sport_name) or "1"   # default soccer

    def run(self):
        data = self.fetch_data()
        data = data.get("doc") or [{}]
        data = data[0].get("data") or {}
        sport_data = data.get("sport") or {}
        countries_in_day = sport_data.get("realcategories") or []
        final_sport_data = {
            "name": self.sport_name,
            "matches": []
        }
        for country in countries_in_day:
            c = self.parse_country(country)
            for match in c:
                final_sport_data["matches"].append(match)
        r.set(f"{self.sport_name}_live_data", json.dumps(final_sport_data))
        return final_sport_data

    def fetch_data(self, date_time=None):
        date_time = date_time or datetime.now().strftime("%Y-%m-%d")

        url = f"https://widgets.fn.sportradar.com/unibet/en/Africa:Johannesburg/gismo/sport_matches/{self.sport_id}/{date_time}"
        headers = {
            'authority': 'widgets.fn.sportradar.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua-mobile': '?0',
            'accept': '*/*',
            'origin': 'https://widgets.sir.sportradar.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://widgets.sir.sportradar.com/',
            'accept-language': 'en-US,en;q=0.9,he;q=0.8'
        }

        content = self.api.request(url=url, headers=headers)
        content = json.loads(content)
        return content

    def parse_country(self, country_data: dict):
        location_data = country_data.get("cc") or {}
        continent = location_data.get("continent") or ""
        country = location_data.get("name") or ""
        leagues = country_data.get("tournaments") or []
        matches_final = []
        meta_dict = {
            "country_name": country,
            "continent": continent,
        }
        for league in leagues:
            league_name = league.get("name") or ""
            if not country and league_name.__contains__("international"):
                country = "international"
            meta_dict["league_name"] = league_name
            matches = league.get("matches") or []
            for match in matches:
                match_dict = self.parse_match(match_data=match, meta_dict=meta_dict)
                matches_final.append(match_dict)
        return matches_final

    @staticmethod
    def parse_match(match_data, meta_dict):
        dt = match_data.get("_dt") or {}
        time_ = dt.get("time")
        date = dt.get("date")
        result_data = match_data.get("result") or {}
        home_res = result_data.get("home")
        home_res = home_res if home_res or home_res == 0 else "?"
        away_res = result_data.get("away")
        away_res = away_res if away_res or away_res == 0 else "?"
        result = f"{home_res}:{away_res}"
        winner = result_data.get("winner") or "?"
        periods = match_data.get("periods")
        teams = match_data.get("teams")
        home = teams.get("home") or {}
        home = home.get("mediumname") or ""
        away = teams.get("away") or {}
        away = away.get("mediumname") or ""
        status = match_data.get("status") or {}
        status = status.get("name") or ""
        cards = match_data.get("cards") or {}
        return {
            "name": f"{home} VS {away}",
            "datetime": f"{date} | {time_}",
            "status": status,
            "result": result,
            "winner": winner
        } | meta_dict


if __name__ == "__main__":
    # x1 = LiveScoresParser("soccer")
    x2 = LiveScoresParser("basketball")
    # x3 = LiveScoresParser("tennis")
    # x4 = LiveScoresParser("table tennis")
    x5 = LiveScoresParser("volleyball")
    # x6 = LiveScoresParser("baseball")
    # for x in [x5]:
    #     res = x.run()
        # with open(f"frontend/scores/src/parsed_sports_data/result_{x.sport_name}.json", "w") as file:
        #     json.dump(res, file, indent=4)
        # print(f"finished {x.sport_name}")

    r = redis.Redis(host='localhost', port=6379, db=0)
    r.set("volleyball_live_data", json.dumps(x2.run()))
