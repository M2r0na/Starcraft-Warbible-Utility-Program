import requests
from bs4 import BeautifulSoup

URL = "https://www.scrmaps.com/cr"


def get_rankings():

    try:

        response = requests.get(
            URL,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        rankings = []

        rows = soup.select("tr.lb-row")

        for row in rows:

            cols = row.find_all("td")

            if len(cols) < 7:
                continue

            # 닉네임 링크 찾기
            player_link = cols[1].find("a")

            if not player_link:
                continue

            rank = cols[0].get_text(
                strip=True
            )

            player = player_link.get_text(
                strip=True
            )

            level = cols[2].get_text(
                strip=True
            )

            crime = cols[3].get_text(
                strip=True
            )

            job = cols[4].get_text(
                strip=True
            )

            weapon = cols[5].get_text(
                strip=True
            )

            upgrade = cols[6].get_text(
                strip=True
            )

            rankings.append({
                "rank": rank,
                "player": player,
                "level": level,
                "crime": crime,
                "job": job,
                "weapon": weapon,
                "upgrade": upgrade
            })

        return rankings

    except Exception as e:

        print(
            f"랭킹 불러오기 실패: {e}"
        )

        return []