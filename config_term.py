from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.common.keys import Keys
import time
import chromedriver_autoinstaller





#print("Digite o IP do equipamento: ")
#host = '192.168.100.145'
#print(host)

def config_term(ip_address):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
#    driver_service = Service(executable_path='/usr/lib/chromedriver')

   # driver = webdriver.Chrome(service=driver_service, options=options)
    
    end_bp = "http://admin:admin@" + ip_address
    driver.get(end_bp)
    time.sleep(5)
    

    print("Acesso ao busca preço, OK!")
    
    ##Configuração padrão
    print("Iniciando configuração padrão.")
    #clicar em Audio
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[3]").click()
    time.sleep(3)
    #Ativa o audio e da OK
                                        
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/fieldset/label[2]/input").click()
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/button").click()
    time.sleep(3)
    
    
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[10]").click()
    time.sleep(3)
    alert = driver.switch_to.alert
    alert.accept()
    print("Audio ativado, OK!")
    print("OK, tudo finalizado!")
    driver.quit()

if __name__ == '__main__':
    config_term()
