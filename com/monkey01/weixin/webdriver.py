#!/usr/bin/python
# coding: utf-8
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

if __name__ == "__main__":
    options = Options()
    options.add_argument('-headless')  # 无头参数
    # driver = Firefox(executable_path='geckodriver', firefox_options=options)
    driver = Chrome(executable_path='chromedriver', chrome_options=options)
    wait = WebDriverWait(driver, timeout=10)
    driver.get('http://mp.weixin.qq.com/s?timestamp=1535431174&src=3&ver=1&signature=*Gm0*FOkQtbAnam*Chw2MD6shvNO2rWk2J-jkFrnHfuXWLjB7ZuIjcPcchdzV1jITsIxZXTH*X3B8-z3DoBht-A0y2lh7RObABTT6hD*xDjUSqr61bbPNbq1qfJhDjBREoWetwbqea060*yZMcVDZ44fUgFeIwVI2ssqQFBdw9s=')
    print(driver.page_source)
    driver.quit()