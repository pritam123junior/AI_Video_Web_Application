from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options

# Path to ChromeDriver (Ensure it's the correct path!)
chrome_driver_path = r"C:\Users\RGON\Downloads\chromedriver-win64\chromedriver.exe"

# Create Chrome Service object
service = Service(chrome_driver_path)

# Set up Chrome options (if needed)
chrome_options = Options()

# Start the Chrome WebDriver with the Service object
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open WhatsApp Web
driver.get("https://web.whatsapp.com/")
input("Scan the QR Code and press Enter...")

# List of numbers
numbers = ["+8801973009007", "+8801234567890"]  # Add more numbers

# Message to send
message = "Hello, this is an automated message from our system."

for number in numbers:
    # Open chat for each number
    url = f"https://web.whatsapp.com/send?phone={number}&text={message}"
    driver.get(url)

    time.sleep(10)  # Wait for chat to load

    try:
        send_button = driver.find_element(By.XPATH, "//button[@data-testid='compose-btn-send']")
        send_button.click()
        print(f"Message sent to {number}")
    except Exception as e:
        print(f"Failed to send message to {number}: {e}")

    time.sleep(5)  # Wait before next message

# Close browser after sending
driver.quit()
