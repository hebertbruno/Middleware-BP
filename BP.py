from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.common.keys import Keys

import chromedriver_autoinstaller
import time


## COnfiguracao do WIFI via Selenium

config = {
    'SSID': 'GFnetwork',
    'SENHA_WIFI': 'ifam@2023#'
}

#print("Digite o IP do equipamento: ")
#host = '192.168.100.145'
#print(host)



def wifi(ip_address):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
   
    end_bp = "http://admin:admin@" + ip_address
    driver.get(end_bp)
    time.sleep(5)
  

    print("Acesso ao busca preço, OK!")

    ##Configuração padrão
    print("Iniciando configuração padrão.")
    #clicar em Rede
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[6]").click()
    time.sleep(2)
    #Muda para Wifi, mantem ip estatico e da OK
                                        
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset[1]/fieldset/label[2]/input").click()
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset[4]/fieldset/label[2]/input").click() 
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/button").click()
    time.sleep(2)
   
  
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[10]").click()
    time.sleep(2)
    alert = driver.switch_to.alert
    alert.accept()
    time.sleep(1)
    print("Configuração padrão, OK!")
    print("OK, tudo finalizado!")
    driver.quit()

if __name__ == '__main__':
    wifi()
