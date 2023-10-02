import pdb
from selenium import webdriver
from selenium.webdriver.common.selenium_manager import SeleniumManager

def main():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    driver.get("https://www.google.com/")
    title = driver.title

    print(title)

if __name__ == "__main__":
    main()