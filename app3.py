from flask import Flask, jsonify, render_template, redirect
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

app = Flask(__name__)

final_page_url = None  # Global variable to store the final URL
driver = None  # Global variable to store WebDriver instance

@app.route('/run', methods=['GET'])
def run_selenium_script():
    global final_page_url, driver
    try:
        print("Starting Selenium script...")

        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")

        # Set up the WebDriver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        print("Chrome WebDriver set up successfully.")

        # Step 1: Log in to Workforce Logiq
        url = 'https://vms.workforcelogiq.com/Login/Login?TabId=3'
        driver.get(url)
        driver.implicitly_wait(30)
        print("Opened Workforce Logiq login page.")

        # Locate the email/username field and enter the email
        email_field = driver.find_element(By.ID, 'Username')
        email_field.send_keys('mvali@askconsulting.com')

        # Locate the password field and enter the password
        password_field = driver.find_element(By.ID, 'Password')
        password_field.send_keys('Greenfr0g!21')

        # Locate and click the "Remember Me" checkbox
        remember_me_checkbox = driver.find_element(By.ID, 'RememberMe')
        remember_me_checkbox.click()

        # Locate and click the "Log In" button
        login_button = driver.find_element(By.CSS_SELECTOR, '.btn.check-submit')
        login_button.click()
        print("Logged in to Workforce Logiq.")

        # Wait for the MFA page to load
        driver.implicitly_wait(30)

        # Step 2: Log in to Outlook
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        url = 'https://outlook.office.com/'
        driver.get(url)
        driver.implicitly_wait(100)
        print("Opened Outlook login page.")

        # Enter Outlook username
        outlook_email_field = driver.find_element(By.NAME, 'loginfmt')
        outlook_email_field.send_keys('kiranmaig@ovahq.com')
        next_button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="idSIButton9" and @value="Next"]')))
        next_button.click()

        # Enter Outlook password
        outlook_password_field = driver.find_element(By.NAME, 'passwd')
        outlook_password_field.send_keys('Gre$np3n8')
        signin_button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="idSIButton9" and @value="Sign in"]')))
        signin_button.click()

        # Click on "Yes" to stay signed in
        yes_button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="idSIButton9" and @value="Yes"]')))
        yes_button.click()
        print("Logged in to Outlook.")

        # Step 3: Retrieve the MFA code from the email
        driver.refresh()
        time.sleep(50)  # Allow time for the page to refresh
        print("Waiting for the email to load.")

        emails = driver.find_elements(By.CSS_SELECTOR, 'div[class="EeHm8"]')
        most_recent_email = emails[1]
        most_recent_email.click()

        email_body = driver.find_element(By.XPATH, '//div[@role="document" and @aria-label="Message body"]')
        verification_code_element = email_body.find_element(By.XPATH, '//td[contains(text(), "is your verification code for Workforcelogiq")]')
        verification_code_text = verification_code_element.text

        verification_code = re.search(r'\d+', verification_code_text).group()
        print(f"Retrieved verification code: {verification_code}")

        # Step 4: Switch back to the Workforce Logiq tab
        driver.switch_to.window(driver.window_handles[0])

        # Enter the 6-digit code in the respective place
        mfa_code_field = WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.XPATH, '//*[@id="VerificationCodeText"]')))
        mfa_code_field.send_keys(verification_code)

        # Locate and click the "Remember this device for 30 days" checkbox
        remember_device_checkbox = driver.find_element(By.XPATH, '//*[@id="RememberDeviceCheckbox"]')
        remember_device_checkbox.click()

        # Locate and click the "Verify" button
        verify_button = driver.find_element(By.XPATH, '//*[@id="verifyChallangeButton"]')
        verify_button.click()
        print("Entered MFA code and verified.")

        # Wait for the final page to load
        driver.implicitly_wait(1000)

        # Get the URL of the final page
        final_page_url = driver.current_url
        print(f"Final page URL: {final_page_url}")

        # Return a success response
        return jsonify({'status': 'success', 'final_page_url': final_page_url})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/final_page', methods=['GET'])
def show_final_page():
    global final_page_url, driver
    if final_page_url:
        # Render the final page content through Flask
        driver.get(final_page_url)
        page_source = driver.page_source
        return page_source
    else:
        return jsonify({'status': 'error', 'message': 'No URL available. Please run the Selenium script first.'})

@app.route('/redirect_final_page', methods=['GET'])
def redirect_to_final_page():
    global final_page_url
    if final_page_url:
        return redirect(final_page_url)
    else:
        return jsonify({'status': 'error', 'message': 'No URL available. Please run the Selenium script first.'})

if __name__ == '__main__':
    app.run(debug=True, host='192.168.31.80',port=8002')
