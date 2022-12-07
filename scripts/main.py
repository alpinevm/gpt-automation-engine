# Automatically load ChatGPT using Selenium and send messages to the chat automatically from templates, and save logs of the chat
from typing import Union, List
import time
import json
import uuid

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class ChatGPTAutomationEngine:
    def __init__(self) -> None:
        self.GPT_CHAT_BASE_URL: str = "https://chat.openai.com/chat"
        self.TEXT_SELECTOR: str = "min-h-[20px] whitespace-pre-wrap flex flex-col items-start gap-4"
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

    def send_message_and_wait_for_response(self, message: str, required_message: Union[str, None] = None, exact_match_if_message_required: bool = True) -> None:
        self.send_message(message)
        self.wait_for_latest_message(required_message, exact_match_if_message_required)

    def get_latest_response(self) -> str:
        return self._patched_find_div_elements(self.TEXT_SELECTOR)[-1].text

    # selenium WebElement().find_elements doesn't seem to work as expected (with class names) so make a function that replaces it
    def _patched_find_div_elements(self, class_name: str) -> List[WebElement]:
        return list(filter(None, [elem if elem.get_attribute('class') == class_name else None for elem in self.driver.find_elements(By.TAG_NAME, "div")]))

    def get_response_to_prompt(self, prompt: str) -> str:
        elements: List[WebElement] = self._patched_find_div_elements(self.TEXT_SELECTOR)
        for index, element in enumerate(elements):
            if element.text == prompt:
                return elements[index + 1].text

    def wait_for_latest_message(self, required_message: Union[str, None] = None, exact_match_if_message_required: bool = True) -> None:
        while(True):
            for button in self.driver.find_elements(By.TAG_NAME, "button"):
                if button.text == 'Try again':
                    if(required_message is None):
                        return
                    if(exact_match_if_message_required and required_message == self.get_latest_response()):
                        return 
                    elif(not exact_match_if_message_required and required_message in self.get_latest_response()):
                        return 
                    else:
                        button.click()
                        self.wait_for_latest_message(required_message, exact_match_if_message_required)
                        return
                        
    def wait_for_keyboard_intterupt(self) -> None:
        input("Press enter to close the browser and save logs...")
    
    def load_chat(self, prompts_file: str) -> None:
        prompts: dict = json.load(open(prompts_file, "r"))
        for prompt in prompts:
            if(prompt.get('acknowledgment', None) is not None):
                self.send_message_and_wait_for_response(prompt['prompt'], prompt['acknowledgment']['response'], prompt['acknowledgment']['exact_match'])
            else:
                self.send_message_and_wait_for_response(prompt['prompt'])
    
    def log_chat(self, log_file: str) -> None:
        log: list = []
        for index, text in enumerate(self._patched_find_div_elements(self.TEXT_SELECTOR)):
            if(index % 2 == 0):
                log.append({"user": {'prompt': text.text}})
                continue
            log.append({"bot": {'response': text.text}})
        open(log_file, "w+").write(json.dumps(log))

    def log_prompt_markdown(self, log_header: str, log_file: str) -> None:
        log: str = f"# {log_header}\n"
        line_number: int =  1
        for index, text in enumerate(self._patched_find_div_elements(self.TEXT_SELECTOR)):
            if(index % 2 == 0):
                log += f"{line_number}. {text.text}\n"
                line_number += 1
        open(log_file, "w+").write(log)
    
    def log_chat_markdown(self, log_header: str, log_file: str) -> None:
        log: str = f"# {log_header}\n"
        for index, text in enumerate(self._patched_find_div_elements(self.TEXT_SELECTOR)):
            if(index % 2 == 0):
                log += f"User: {text.text}\n"
            else:
                log += f"Bot: {text.text}\n"
        open(log_file, "w+").write(log)

if __name__ == "__main__":
    gpt: ChatGPTAutomationEngine = ChatGPTAutomationEngine()
    gpt.load_chat("templates/sentient.json")
    gpt.wait_for_keyboard_intterupt()
    gpt.log_chat(f"logs/{str(uuid.uuid4())}.json")
    gpt.log_prompt_markdown("Chat Prompts", f"logs/sentient_prompts.md")
    gpt.log_chat_markdown("Chat Log", f"logs/sentient_chat.md")