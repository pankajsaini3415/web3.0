from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
options = Options()
options.add_argument("--start-maximized")

# Set up the WebDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Opening Telegram Web...")
    driver.get("https://web.telegram.org/a/")

    # Wait for the Start Messaging button and click it
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='auth-qr-form']/div/button"))
    ).click()
    print("Clicked Start Messaging button.")

    # Wait for the phone number input field and enter the phone number
    phone_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='sign-in-phone-number']"))
    )
    phone_number = "+91 6377567792"  # Replace with your phone number
    phone_input.send_keys(phone_number)
    print("Entered phone number.")

    # Wait for the Next button and click it
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='auth-phone-number-form']/div/form/button[1]"))
    ).click()
    print("Clicked Next button.")

    # Prompt user to enter the verification code (OTP) in the terminal
    otp = input("Please enter the OTP sent to your phone: ")

    # Wait for the OTP input field and enter the OTP
    otp_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='auth-pages']/div/div[2]/div[4]/div/div[3]/div/input"))  # Adjust the XPath as needed
    )
    otp_input.send_keys(otp)
    print("Entered OTP.")

    # (Optional) Click the final login button if needed
    final_login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='auth-code-form']/div/form/button"))
    )
    final_login_button.click()
    print("Clicked Login button.")

    # Wait for user to manually complete the login process (if needed)
    input("Press Enter to close the browser...")

finally:
    driver.quit()
