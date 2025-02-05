import time
from dataclasses import dataclass
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re

@dataclass
class FortuneWebsiteInfo:
    updated: Optional[str] = None
    country: Optional[str] = None
    headquarters: Optional[str] = None
    industry: Optional[str] = None
    ceo: Optional[str] = None
    website: Optional[str] = None
    ticker: Optional[str] = None
    company_type: Optional[str] = None
    revenues: Optional[float] = None  # Assuming revenues are numerical
    profits: Optional[float] = None
    market_value: Optional[float] = None
    employee_count: Optional[int] = None
    revenues_m: Optional[float] = None
    profits_m: Optional[float] = None  # Profits ($M)
    assets_m: Optional[float] = None  # Assets ($M)
    stockholder_equity_m: Optional[float] = None  # Total Stockholder Equity ($M)
    profit_margin: Optional[float] = None  # Profit as % of Revenues
    profit_as_percent_assets: Optional[float] = None  # Profits as % of Assets
    profit_as_percent_equity: Optional[float] = None  # Profits as % of Stockholder Equity



def execute_on_web_element(driver, xpath, action, index=-1):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    if index == -1:
        index = len(driver.find_elements(By.XPATH, xpath)) - 1
    element = driver.find_elements(By.XPATH, xpath)[index]
    return action(element)


def parse_fortune_text(raw_text: str) -> FortuneWebsiteInfo:
    raw_text = raw_text.replace('$ Millions% change', '')
    patterns = [
        "Updated:",
        "Country:",
        "Headquarters:",
        "Industry:",
        "CEO:",
        "Website:",
        "Ticker:",
        "Company type:",
        "Revenues ($M):",
        "Profits ($M):",
        "Market value ($M):",
        "Number of employees:",
        "Revenues ($M):",
        "Profits ($M):",
        "Assets ($M):",
        "Total Stockholder Equity ($M):",
        "Profit as % of Revenues:",
        "Profits as % of Assets:",
        "Profits as % of Stockholder Equity:"
    ]

    extracted_data = []
    parsed_data = []
    raw_text_copy = raw_text
    try:
        for i, current_pattern in enumerate(patterns):
            if i == 13:
                pass
            next_pattern = patterns[min(i + 1, len(patterns)-1)]
            extraction = raw_text_copy.split(current_pattern)[1].split(next_pattern)[0]
            extracted_data.append(extraction)
            raw_text_copy = raw_text_copy.split(current_pattern, 1)[1]

        parsed_data = FortuneWebsiteInfo(*extracted_data)
    except Exception as e:
        pass
    return parsed_data


class FortuneWebScraper:
    def __init__(self, driver=None):
        if driver is None:
            # Start Driver
            chrome_options = Options()
            chrome_options.add_argument("--disable-notifications")
            # chrome_options.add_argument('--headless=new')
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            self.driver = driver

    def scrape_website(self, fortune_url):
        self.driver.get(fortune_url)
        if fortune_url=="https://fortune.com/company/abbvie/":
            pass
        # Slurp company info
        xpath = "//span[text()='Headquarters']/../../.."
        company_info = execute_on_web_element(self.driver, xpath, lambda f: self.driver.execute_script("return arguments[0].textContent.trim();",f),0)

        # Slurp key financials
        xpath = "//span[text()='Total Stockholder Equity ($M)']/../../.."
        key_financials = execute_on_web_element(self.driver, xpath, lambda f: self.driver.execute_script("return arguments[0].textContent.trim();",f),0)

        # Slurp profit ratios
        xpath = "//span[text()='Profits as % of Stockholder Equity']/../../.."
        profit_ratios = execute_on_web_element(self.driver, xpath, lambda f: self.driver.execute_script("return arguments[0].textContent.trim();",f),0)

        return parse_fortune_text(f"{company_info}{key_financials}{profit_ratios}")
