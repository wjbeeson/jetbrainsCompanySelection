import json
import csv
from fortune_scraper import FortuneWebScraper, FortuneWebsiteInfo

with open('fortune_links.json') as fl:
    links = json.load(fl)


fortune_scraper = FortuneWebScraper()
data_rows = []

# Scrape each link and store results
for link in links:
    info_class = fortune_scraper.scrape_website(link)

    info_dict = info_class.__dict__

    info_dict["link"] = link

    data_rows.append(info_dict)


csv_filename = "fortune_companies.csv"

# Write to CSV file
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["link"] + list(FortuneWebsiteInfo.__annotations__.keys()))
    writer.writeheader()
    writer.writerows(data_rows)

print(f"Data successfully saved to {csv_filename}")
