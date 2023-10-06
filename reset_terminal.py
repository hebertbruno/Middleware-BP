from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.common.keys import Keys

import chromedriver_autoinstaller
import time


## Restaura configuracao de fabrica

def reset_terminal(ip_address):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
   
    end_bp = "http://admin:admin@" + ip_address
    driver.get(end_bp)
    time.sleep(3)
    
    print("Acesso ao busca preço, OK!")
    
    print("Restaurando padrao de fabrica.")
    
    #clicar em Restaurar Configuracoes
    
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[9]").click()
    time.sleep(2)
    alert = driver.switch_to.alert
    alert.accept()
    time.sleep(1)
    print("Padrão de Fabrica restaurado, OK!")
    print("OK, tudo finalizado!")
    #driver.quit()

if __name__ == '__main__':
    reset_terminal()
