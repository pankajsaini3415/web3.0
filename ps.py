from selenium import webdriver
import winsound 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from multiprocessing import Process

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
        print("Input box filled with:", input_value)
        WebDriverWait(driver, 2).until(EC.text_to_be_present_in_element((By.XPATH, input_xpath), input_value))
    except (TimeoutException, NoSuchElementException) as e:
        print("Input box not found or took too long to load:", e)

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
        print("Error fetching first page values and links:", e)
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
        print("Value from the second  div:", second_div_value)
        process_div_value(div_value, second_div_value, input_value, first_div_value, anchor_link)
    except (TimeoutException, NoSuchElementException) as e:
        print("Div not found or took too long to load:", e)
        winsound.Beep(1000, 500)
        with open("wndata.txt", "a") as file:
                file.write(f"Input Value: {input_value}\n")
                file.write(f"First Page Div Value: {first_div_value}\n")
                file.write(anchor_link + "\n")
                print(f"Anchor link saved to data.txt: {anchor_link}")
    finally:
        driver.close()  # Close the new tab
        driver.switch_to.window(driver.window_handles[0])  # Switch back to the original tab

# Function to process the div value
def process_div_value(div_value, second_div_value, input_value, first_div_value, anchor_link):
    try:
        div_value_float = float(div_value)
        second_div_value_float = float(second_div_value)
        print("Converted second div value to float:", second_div_value_float)
        print(" div value :", first_div_value)

        if second_div_value_float > 0:
            winsound.Beep(1000, 5000)
            with open("nndata.txt", "a") as file:
                file.write(f"Input Value: {input_value}\n")
                file.write(f"First Page Div Value: {first_div_value}\n")
                file.write(anchor_link + "\n")
            print(f"Anchor link saved to data.txt: {anchor_link}")
        else:
            # winsound.Beep(1000, 200)
            print("Div value is not greater than 0, link will not be saved.")
    except ValueError:
        print(f"Could not convert '{div_value}' to float.")

# Function to handle a single input value
def handle_input_value(input_value):
    driver = init_driver()
    try:
        driver.get("https://zengo-x.github.io/mnemonic-recovery/src/index.html")
        words = input_value.split()
        
        for i in range(len(words)):
            modified_input = input_value.replace(words[i], '?', 1)
            print("Generated input:", modified_input)
            
            # Fill the input box and wait for the process to complete
            fill_input_box(driver, modified_input)
            
            # Wait for the first page values to be loaded
            first_page_values, anchor_links = get_first_page_values_and_links(driver)

            if not first_page_values or not anchor_links:
                print("No values or links found for input:", modified_input)
                continue  # Skip to the next input if none found

            for first_div_value, anchor_link in zip(first_page_values, anchor_links):
                handle_anchor_link(driver, anchor_link, modified_input, first_div_value)

    except Exception as e:
        print("An error occurred:", e)  # Catch any unhandled exceptions
    finally:
        driver.quit()

def main():
    input_values = [
        "reward focus client cram flavor clean vast man hood brisk error document",
        "evidence since say earn float engage expand slight when knife vibrant weapon",
        "juice wild jewel elephant search response crouch trumpet frost domain vast bundle",
        "once digital boost veteran nominee muscle inflict myself entry raw lounge rhythm"
      
        # "flavor clean vast man hood brisk error document once digital boost veteran",
        # "float engage expand slight when knife vibrant weapon juice wild jewel elephant",
        # "search response crouch trumpet frost domain vast bundle evidence since say earn",
        # "nominee muscle inflict myself entry raw lounge rhythm reward focus client cram"
    ]
    
    processes = []
    for input_value in input_values:
        process = Process(target=handle_input_value, args=(input_value,))
        processes.append(process)
        process.start()  # Start the process

    # Wait for all processes to complete
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
