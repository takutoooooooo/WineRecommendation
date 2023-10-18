import requests
import pandas as pd

def get_wine_data(wine_id, year, page):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    api_url = "https://www.vivino.com/api/wines/{id}/reviews?per_page=50&year={year}&page={page}"  # <-- increased the number of reviews to 9999
    data = requests.get(
        api_url.format(id=wine_id, year=year, page=page), headers=headers
    ).json()
    return data

number_page = [1]
country_codes = ["nl"]

for wine_page in number_page:
    for country_code in country_codes:
        r = requests.get(
            "https://www.vivino.com/api/explore/explore",
        params={                   
            "country_code": "FR",
            "country_codes[]": country_code,
            "currency_code": "EUR",
            "grape_filter": "varietal",
            "min_rating": "1",
            "page": wine_page,
            "order_by": "ratings_count",
            "wine_type_ids[]": "1",
        },
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
        },
        )

        results = []
        for t in r.json()["explore_vintage"]["matches"]:
            winery_name = t["vintage"]["wine"]["winery"]["name"]
            year = t["vintage"]["year"]
            wine_id = t["vintage"]["wine"]["id"]
            wine_name_year = f'{t["vintage"]["wine"]["name"]} {t["vintage"]["year"]}'
            ratings_average = t["vintage"]["statistics"]["ratings_average"]
            ratings_count = t["vintage"]["statistics"]["ratings_count"]
        
            if t["vintage"]["wine"]["taste"] and t["vintage"]["wine"]["taste"]["structure"]:
                acidity = t["vintage"]["wine"]["taste"]["structure"].get("acidity")
                fizziness = t["vintage"]["wine"]["taste"]["structure"].get("fizziness")
                intensity = t["vintage"]["wine"]["taste"]["structure"].get("intensity")
                sweetness = t["vintage"]["wine"]["taste"]["structure"].get("sweetness")
                tannin = t["vintage"]["wine"]["taste"]["structure"].get("tannin")

            else:
                acidity = None  # acidityが存在しない場合はNoneを設定
                fizziness = None
                intensity = None
                sweetness = None
                tannin = None

            results.append((winery_name, year, wine_id, wine_name_year, ratings_average, ratings_count, acidity, fizziness, intensity, sweetness, tannin))

        wine_df = pd.DataFrame(
            results,
            columns=["Winery", "Year", "Wine ID", "Wine", "Rating", "num_review", "acidity", "fizziness", "intensity", "sweetness", "tannin"],
        )
        ratings = []
        for _, row in wine_df.iterrows():
            page = 1
            while True:
                print(
                    f'Getting info about wine {row["Wine ID"]}-{row["Year"]} Page {page}'
                )
                d = get_wine_data(row["Wine ID"], row["Year"], page)
                if not d["reviews"]:
                    break
                for r in d["reviews"]:
                    ratings.append(
                        [
                            row["Year"],
                            row["Wine ID"],
                            r["rating"],
                            r["created_at"],
                            r["user"]["id"],
                        ]
                    )
                page += 1
        ratings_df = pd.DataFrame(
            ratings, columns=["Year", "Wine ID", "User Rating", "CreatedAt", "userID"]
        )
        ratings_df.to_csv(f"data/user_review_{country_code}_{wine_page}.csv", index=False)
        wine_df.to_csv(f"data/wine_data_global_{country_code}_{wine_page}.csv", index=False)
