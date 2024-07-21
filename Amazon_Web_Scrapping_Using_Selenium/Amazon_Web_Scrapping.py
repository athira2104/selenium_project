from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import streamlit as st
# Path to your chromedriver
path = 'C://chromedriver.exe'

driver = webdriver.Chrome()
driver.get("https://www.amazon.in")
time.sleep(2)


# Lists to store data
headings = []
prices = []
ratings = []
num_ratings = []

# Function to process product links and collect data
def process_product_links():
    # Wait for the product list to load
    product_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//h2/a"))
    )

    # Iterate over product links
    for product_link in product_links:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", product_link)  # Scroll to the product link
            driver.execute_script("arguments[0].click();", product_link)
            time.sleep(2)  # Give time for the new tab to open
            original_window = driver.current_window_handle

            # Switch to the new window
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    break

            # Extract product details
            heading = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "productTitle"))
            ).text

            # Try to locate the price using various XPaths
            price_element = None
            price_xpaths = [
                "//span[@id='priceblock_ourprice']",
                "//span[@id='priceblock_dealprice']",
                "//span[contains(@class, 'priceToPay')]",
                "//span[contains(@class, 'priceBlockBuyingPriceString')]",
                "//span[contains(@class, 'a-size-medium a-color-price priceBlockBuyingPriceString')]"
            ]
            for xpath in price_xpaths:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    price_element = elements[0]
                    break

            price = price_element.text if price_element else "N/A"

            # Extract rating
            try:
                rating_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='acrPopover']"))
                )
                rating = rating_element.get_attribute("title")
            except:
                rating = "N/A"

            # Extract number of ratings
            try:
                num_raters_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@id='acrCustomerReviewText']"))
                )
                num_raters = num_raters_element.text
            except:
                num_raters = "N/A"

            # Append to lists
            headings.append(heading)
            prices.append(price)
            ratings.append(rating)
            num_ratings.append(num_raters)

            # Close the new window and switch back to the original window
            driver.close()
            driver.switch_to.window(original_window)
            time.sleep(2)  # Ensure the switch is complete before continuing
        except Exception as e:
            print(f"Error processing link: {e}")
            continue

page_number = 1
while True:
    process_product_links()
    try:
        if page_number == 1:
            next_button_xpath = "/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[30]/div/div/span/a[3]"
        elif page_number in range(2,5):
            next_button_xpath = f"/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[29]/div/div/span/a[{page_number + 2}]"
        else:
            next_button_xpath = "/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[29]/div/div/span/a[5]"

        next_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, next_button_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        print(f"Clicked on next button for page {page_number}")
        time.sleep(10)
        page_number += 1
    except Exception as e:
        print(f"No more pages or error: {e}")
        break
# Close the driver
driver.quit()

# Create DataFrame
df = pd.DataFrame({
    'Heading': headings,
    'Price': prices,
    'Rating': ratings,
    'No Of Raters': num_ratings
})

# Save DataFrame to CSV file
df.to_csv('amazon_laptops.csv', index=False)

# Save DataFrame to Excel file
df.to_excel('amazon_laptops.xlsx', index=False)

print(df)