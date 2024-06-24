import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
import time
import pandas as pd
from datetime import datetime
import os
from lxml import html
import pandas as pd

file_path = "input_list.csv"


def get_text(browser, xpath, wait_time=0):
    #Extracts text context from an element using the provided XPath
    try:
        if wait_time:
            return WebDriverWait(browser, wait_time).until(EC.visibility_of_element_located((By.XPATH, xpath))).text
        return browser.find_element(By.XPATH, xpath).text
    except (NoSuchElementException, TimeoutException) as e:
        return ""


def main_scrapper(url):
    """
    Function to extract ALL details .
    """
    job_data = []

    
    with uc.Chrome() as browser:
        browser.get(url)
        time.sleep(2)

        tree = html.fromstring(browser.page_source)
        
        try:
            # Append data to the list
            job_data.append({
                "Title of the Book": get_text(browser, '//h1[@class="MuiTypography-root MuiTypography-h1 mui-style-1ngtbwk"]'),
                "Author/s": get_text(browser, '//span[@class="MuiTypography-root MuiTypography-body1 mui-style-1plnxgp"]'),
                "Book type": get_text(browser, '//div[@class="MuiBox-root mui-style-1ebnygn"]//p[@class="MuiTypography-root MuiTypography-body1 mui-style-tgrox"]').split("|")[0].strip(),
                "Book price": get_text(browser, '//div[@data-testid="related-products"]//p[contains(normalize-space(), "Book") and not(contains(normalize-space(), "eBook"))]/following-sibling::p'),
                "eBook Price": get_text(browser, '//div[@class="MuiStack-root BuyBox_center-price__fXF15 mui-style-j7qwjs"] | //div[@data-testid="related-products"]//p[contains(.,"eBook")]/following-sibling::p'),
                "Audio_Book_Price": get_text(browser, '//div[@data-testid="related-products"]//p[contains(.,"Audiobook")]/following-sibling::p'),
                "Discounted price": 'No discount', 
                "ISBN_10": ''.join(tree.xpath('//p[span[contains(., "ISBN-10")]]/span/following-sibling::text()')),
                "Published_Date": datetime.strptime(get_text(browser, '//div[@class="MuiBox-root mui-style-1ebnygn"]//p[@class="MuiTypography-root MuiTypography-body1 mui-style-tgrox"]').split("|")[-1].strip(), "%d %B %Y").strftime("%Y-%m-%d"),
                "Publisher": ''.join(tree.xpath('//p[span[contains(., "Publisher")]]/span/following-sibling::text()')),
                "No. of Pages": ''.join(tree.xpath('//p[span[contains(., "Number of Pages")]]/span/following-sibling::text()')),
                "Book URL": url,
            })
        except:
            job_data = pd.DataFrame()

    browser.quit()
    return job_data


if __name__ == "__main__":

    df = pd.read_csv(file_path, nrows=5)  # DATA SCRAPED FOR 5 BOOKS ONLY

    for isbn in df['ISBN13']:
        url = f"https://www.booktopia.com.au/book/{isbn}.html"
        job_data = main_scrapper(url)

        file_path = "booktopia_data.csv"
        file_exists = os.path.isfile(file_path)

        df = pd.DataFrame(job_data)
        if file_exists:
            df.to_csv(file_path, mode='a', index=False, header=False)
        else:
            df.to_csv(file_path, mode='w', index=False, header=True)

        if len(job_data) == 0:
            print(url, " : NO DATA")
        else:
            print(url ," : DATA INSERTED")