import random
import time
import winsound  # Only available on Windows
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from multiprocessing import Process
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load words from a text file
def load_words(file_path):
    """Load words from a text file."""
    with open(file_path, 'r') as file:
        words = file.read().splitlines()
    return words

# Function to create random phrases from the words
def create_random_phrases(words, num_phrases=4, phrase_length=12):
    """Create a specified number of random phrases from the given words."""
    phrases = []
    for _ in range(num_phrases):
        phrase = random.sample(words, phrase_length)
        phrases.append(' '.join(phrase))
    return phrases

# Function to initialize the Chrome driver
def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment for headless mode
    service = Service(executable_path="chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

# Function to fill the input box
def fill_input_box(driver, input_value):
    input_xpath = "//*[@id='phrase']"
    try:
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, input_xpath))
        )
        input_box.clear()
        input_box.send_keys(input_value)
        logging.info("Input box filled with: %s", input_value)
        WebDriverWait(driver, 2).until(EC.text_to_be_present_in_element((By.XPATH, input_xpath), input_value))
    except (TimeoutException, NoSuchElementException) as e:
        logging.error("Input box not found or took too long to load: %s", e)

# Function to get values from the first page and corresponding anchor links
def get_first_page_values_and_links(driver):
    div_xpath_first_page = "/html/body/div/div[1]/div[1]/form/table/tbody/tr"
    try:
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, div_xpath_first_page))
        )
        first_page_values = []
        anchor_links = []

        for row in rows:
            first_div_value = row.find_element(By.XPATH, "./td[1]").text  # Adjust index as necessary
            anchor_element = row.find_element(By.XPATH, "./td[5]/a")  # Adjust index as necessary
            anchor_link = anchor_element.get_attribute('href')

            first_page_values.append(first_div_value)
            anchor_links.append(anchor_link)

        return first_page_values, anchor_links
    except (TimeoutException, NoSuchElementException) as e:
        logging.error("Error fetching first page values and links: %s", e)
        return [], []

# Function to handle each anchor link in a new tab
def handle_anchor_link(driver, anchor_link, input_value, first_div_value):
    driver.execute_script("window.open(arguments[0], '_blank');", anchor_link)
    driver.switch_to.window(driver.window_handles[1])
    try:
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, "Prcrh")))  # Adjust class name as needed
        second_div_xpath = "//*[@id='__next']/div[2]/div[2]/main/div/div/div/div[4]/div/div[1]/div[2]/div[2]/div[6]/div[2]"
        second_div_element = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, second_div_xpath))
        )
        second_div_value = second_div_element.text
        div_value = driver.find_element(By.CLASS_NAME, "Prcrh").text  # Adjust class name as needed
        logging.info("Value from the second div: %s", second_div_value)
        process_div_value(div_value, second_div_value, input_value, first_div_value, anchor_link)
    except (TimeoutException, NoSuchElementException) as e:
        logging.error("Div not found or took too long to load: %s", e)
        winsound.Beep(1000, 3000)
        with open("wnndata.txt", "a") as file:
            file.write(f"Input Value: {input_value}\n")
            file.write(f"First Page Div Value: {first_div_value}\n")
            file.write(anchor_link + "\n")
            logging.info("Anchor link saved to data.txt: %s", anchor_link)
    finally:
        driver.close()  # Close the new tab
        driver.switch_to.window(driver.window_handles[0])  # Switch back to the original tab

# Function to process the div value
def process_div_value(div_value, second_div_value, input_value, first_div_value, anchor_link):
    try:
        div_value_float = float(div_value)
        second_div_value_float = float(second_div_value)
        logging.info("Converted second div value to float: %s", second_div_value_float)
        logging.info("Div value: %s", first_div_value)

        # Condition to play beep and save data
        if second_div_value_float > 0:  # Adjust your condition as needed
            winsound.Beep(1000, 3000)  # Frequency and duration in milliseconds
            with open("nndata.txt", "a") as file:
                file.write(f"Input Value: {input_value}\n")
                file.write(f"First Page Div Value: {first_div_value}\n")
                file.write(anchor_link + "\n")
            logging.info("Anchor link saved to data.txt: %s", anchor_link)
        else:
            logging.info("Div value is not greater than 0, link will not be saved.")
    except ValueError:
        logging.error("Could not convert '%s' to float.", div_value)

# Function to handle a single input value
def handle_input_value(input_value):
    driver = init_driver()
    try:
        driver.get("https://zengo-x.github.io/mnemonic-recovery/src/index.html")
        words = input_value.split()
        
        for i in range(len(words)):
            modified_input = input_value.replace(words[i], '?', 1)
            logging.info("Generated input: %s", modified_input)
            fill_input_box(driver, modified_input)
            
            # Wait for the first page values to be loaded
            first_page_values, anchor_links = get_first_page_values_and_links(driver)

            if not first_page_values or not anchor_links:
                logging.warning("No values or links found for input: %s", modified_input)
                continue  # Skip to the next input if none found

            for first_div_value, anchor_link in zip(first_page_values, anchor_links):
                handle_anchor_link(driver, anchor_link, modified_input, first_div_value)

    except Exception as e:
        logging.error("An error occurred: %s", e)  # Catch any unhandled exceptions
    finally:
        driver.quit()

def main():
    file_path = 'phaseword.txt'
    words = load_words(file_path)

    while True:
        if len(words) < 12:
            logging.warning("Not enough words in the file to create 12-word phrases.")
            break

        phrases = create_random_phrases(words)
        processes = []  # List to keep track of processes

        for i, phrase in enumerate(phrases, start=1):
            logging.info("Generated Phrase %d: %s", i, phrase)
            process = Process(target=handle_input_value, args=(phrase,))
            processes.append(process)  # Add process to the list
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()

        time.sleep(10)  # Adjust time as needed before generating new phrases

if __name__ == "__main__":
    main()
