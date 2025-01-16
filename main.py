import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def setup_driver():
    service = Service("chromedriver.exe")
    browser = webdriver.Chrome(service=service)
    browser.maximize_window()
    return browser

def wait_for_element(browser, xpath, timeout=20):
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

def wait_for_element_to_be_interactable(browser, xpath, timeout=20):
    return WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )

def navigate_to_chat(browser, chat_name):
    search_box = wait_for_element(browser, '//div[@contenteditable="true"][@data-tab="3"]')
    
    search_box = wait_for_element_to_be_interactable(browser, '//div[@contenteditable="true"][@data-tab="3"]')
    
    search_box.send_keys(Keys.CONTROL, 'a')
    search_box.send_keys(Keys.BACKSPACE)
    
    time.sleep(1)
    
    pyperclip.copy(chat_name)
    search_box.send_keys(Keys.CONTROL, 'v')
    time.sleep(2)
    
    chat_xpath = f'//span[@title="{chat_name}"]'
    try:
        chat_element = wait_for_element(browser, chat_xpath)
        chat_element.click()
        time.sleep(2)
        print(f"Navigated to {chat_name}")
    except Exception as e:
        print(f"Error navigating to {chat_name}: {e}")
        return False
    return True

def get_latest_messages(browser, last_message=""):
    try:
        messages = browser.find_elements(By.CSS_SELECTOR, 'div._akbu')
        
        if not messages:
            return []

        message_texts = []
        found_last_message = False

        for msg in messages:
            try:
                text = msg.text
                
                if found_last_message:
                    message_texts.append(text)
                elif text == last_message:
                    found_last_message = True
                
            except Exception as e:
                continue
        return message_texts
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []

def send_message(browser, message):
    try:
        message_box = wait_for_element(browser, '//div[@contenteditable="true"][@data-tab="10"]')
        
        message_box.send_keys(message + Keys.ENTER)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def main():
    source_chat = "Me"  # Set your source chat here
    target_chat = "P😂"  # Set your target chat here
    
    last_processed_message = "start"
    
    browser = setup_driver()
    try:
        browser.get('https://web.whatsapp.com/')
        print("Please scan the QR code to login")
        
        wait_for_element(browser, '//div[@contenteditable="true"][@data-tab="3"]', 60)
        print("Successfully logged in!")
        time.sleep(2)

        print(f"Starting message forwarding from '{source_chat}' to '{target_chat}'")
        print("Press Ctrl+C to exit")
        
        while True:
            try:
                if not navigate_to_chat(browser, source_chat):
                    print(f"Failed to reach source chat '{source_chat}'. Skipping cycle.")
                    time.sleep(5)
                    continue
                
                new_messages = get_latest_messages(browser, last_processed_message)
                
                if new_messages:
                    print(f"Found {len(new_messages)} new messages")
                    
                    if not navigate_to_chat(browser, target_chat):
                        print(f"Failed to reach target chat '{target_chat}'. Skipping forwarding this message.")
                        continue
                    
                    for message in new_messages:
                        if send_message(browser, message):
                            print(f"Forwarded message: {message}")
                            last_processed_message = message
                        else:
                            print("Failed to forward message")
                            break
                
                if not navigate_to_chat(browser, source_chat):
                    print(f"Failed to return to source chat '{source_chat}'. Skipping cycle.")
                    time.sleep(5)
                    continue

                time.sleep(5)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        print("\nStopping message forwarder...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
