# Automatically load ChatGPT using Selenium and send messages to the chat to make it sentient
from typing import Union
import time
import json

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class AutoChatGPT:
    def __init__(self) -> None:
        self.GPT_CHAT_BASE_URL: str = "https://chat.openai.com/chat"
        # change this to whatever browser you want to use
        self.driver: Chrome  = webdriver.Chrome()
        # go to a random page to allow cookies to be set

        self.driver.get(self.GPT_CHAT_BASE_URL)

        # try to set cookies
        self._try_set_cookies()

        # go to the chat
        self.driver.get(self.GPT_CHAT_BASE_URL)

        self._wait_for_input_box_render()
        
        
        self._update_cookies()

        self._close_dialog()

        # good to go!

    def _wait_for_input_box_render(self) -> None:
        while(True):
            try:
                self.driver.find_element(By.TAG_NAME, "textarea")
                break
            except NoSuchElementException:
                time.sleep(1)

    def _close_dialog(self) -> None:
        # doing this based on explicit class name didn't work so I'm doing it recursively based on the text for now
        for element in self.driver.find_elements(By.TAG_NAME, "button"):
            if element.text == "Next" or element.text == "Done":
                element.click()
                time.sleep(.1)
                self._close_dialog()
                break    

    def _get_saved_cookies(self) -> dict:
        try:
            return json.loads(open("cookies.json", "r").read())
        except FileNotFoundError:
            return {}

    def _try_set_cookies(self) -> None:
        cookies = self._get_saved_cookies()
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(cookie)
                print(e)

    def _update_cookies(self) -> None:
        open("cookies.json", "w").write(json.dumps(self.driver.get_cookies()))

    def send_message(self, message: str) -> None:
        input_box = self.driver.find_element(By.TAG_NAME, "textarea")
        input_box.send_keys(message)
        input_box.send_keys(Keys.ENTER)
    
    def get_latest_message_text(self) -> str:
        # TODO: Work on this
        return self.driver.find_elements(By.TAG_NAME, "p")

    def wait_for_latest_message(self, required_message: Union[str, None] = None, exact_match_if_message_required: bool = True) -> None:
        while(True):
            for button in self.driver.find_elements(By.TAG_NAME, "button"):
                if button.text == 'Try again':
                    if(required_message is None):
                        return
                    if(exact_match_if_message_required and required_message == self.get_latest_message_text()):
                        return 
                    elif(not exact_match_if_message_required and required_message in self.get_latest_message_text()):
                        return 
                    else:
                        button.click()
                        self.wait_for_latest_message(required_message, exact_match_if_message_required)
                        return
            time.sleep(1)

    def wait_for_keyboard_intterupt(self) -> None:
        while(True):
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
    
if __name__ == "__main__":
    gpt: AutoChatGPT = AutoChatGPT()
    gpt.send_message("Hello GPT!")
    gpt.wait_for_latest_message()
    time.sleep(30)
    text = gpt.get_latest_message_text()
    for t in text:
        
        print(t.text)