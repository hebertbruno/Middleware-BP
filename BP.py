from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.common.keys import Keys

import chromedriver_autoinstaller
import time



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
#    driver_service = Service(executable_path='/usr/lib/chromedriver')

   # driver = webdriver.Chrome(service=driver_service, options=options)
    
    end_bp = "http://admin:admin@" + ip_address
    driver.get(end_bp)
    time.sleep(5)
    # try:
    #     alert = driver.switch_to.alert

    #     # Enviar o valor do usuário para o prompt box
    #     alert.send_keys(config['USER'])
    #     alert.send_keys('\t')
    #     alert.send_keys(config['SENHA'])

    #     # Aceitar o prompt box
    #     alert.accept()

    print("Acesso ao busca preço, OK!")
    # except NoAlertPresentException:
    # print("Nenhum prompt box encontrado")

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
    
    #clica na aba Wifi
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[7]").click()
    #
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/p[1]/input")
    elem.click()
    elem.clear()
    elem.send_keys(config['SSID'])
    time.sleep(2)
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/p[2]/input[2]").click()
    time.sleep(2)
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/p[2]/input[1]")
    elem.click()
    senha_wifi= list(config["SENHA_WIFI"])
    
    if elem is not None:
        elem.clear()  # Limpa o campo de input
        elem.send_keys(*senha_wifi)
    else:
        print("Elemento não encontrado.")
    #print(elem.send_keys(config['SENHA_WIFI']))
    print(config['SENHA_WIFI'])
    time.sleep(2)
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/button").click()
    time.sleep(2)
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[10]").click()
    time.sleep(2)
    alert = driver.switch_to.alert
    alert.accept()
    print("Configuração padrão, OK!")
    print("OK, tudo finalizado!")
    driver.quit()

if __name__ == '__main__':
    wifi()
