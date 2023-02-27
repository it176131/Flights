from datetime import datetime
from pathlib import Path

from scrapy import Spider
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ..http import SeleniumRequest


class GoogleSpider(Spider):
    name = "google"
    allowed_domains = "google.com/travel/flights"
    start_urls = ["https://www.google.com/travel/flights"]
    origin = None
    destination = None

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.select)

    def select(self, response, **kwargs):
        if self.origin is None and self.destination is None:
            raise ValueError("Must supply at least one of `origin` or "
                             "`destination`.")

        driver: WebDriver = response.request.meta["driver"]
        wait = WebDriverWait(driver=driver, timeout=10)
        actions = ActionChains(driver=driver)

        if self.origin is not None:
            self.logger.info(f"Origin: {self.origin}")
            origin_input = driver.find_element(
                by="xpath",
                value="//input[@placeholder='Where from?']"
            )
            actions.click(origin_input)
            actions.pause(1)
            actions.send_keys(self.origin)
            actions.pause(1)
            actions.send_keys(Keys.ENTER)
            actions.pause(1)
            actions.perform()
            actions.reset_actions()

        if self.destination is not None:
            self.logger.info(f"Destination: {self.destination}")
            destination_input = driver.find_element(
                by="xpath",
                value="//input[@placeholder='Where to?']"
            )
            actions.click(destination_input)
            actions.pause(1)
            actions.send_keys(self.destination)
            actions.pause(1)
            actions.send_keys(Keys.ENTER)
            actions.pause(1)
            actions.perform()
            actions.reset_actions()

        # search_button
        search_button = wait.until(
            method=EC.presence_of_element_located(
                (By.XPATH, "//button[@aria-label='Search for flights']")
            )
        )
        search_button.click()

        yield SeleniumRequest(
            wait_time=5,  # wait until page is loaded
            url=driver.current_url,
            callback=self.save_results,
            dont_filter=True
        )

    def save_results(self, response, **kwargs):
        driver: WebDriver = response.request.meta["driver"]
        wait = WebDriverWait(driver=driver, timeout=10)
        wait.until(
            method=EC.presence_of_element_located(
                (By.XPATH, "//div[@role='main']/div[@role='alert']")
            )
        )
        dttm = datetime.now().strftime("%Y%m%d_%H%M%S")
        response_html = Path(f"response_html")
        response_html.mkdir(parents=True, exist_ok=True)
        path = response_html / f"response_{dttm}.html"
        with path.open(mode="w", encoding="utf-8") as f:
            f.write(response.text)
