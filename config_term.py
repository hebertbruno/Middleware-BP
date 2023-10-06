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

def config_term(ip_address, ip_local, ssid, senha_wifi, porta):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
#    driver_service = Service(executable_path='/usr/lib/chromedriver')

   # driver = webdriver.Chrome(service=driver_service, options=options)
    
    end_bp = "http://admin:admin@" + ip_address
    driver.get(end_bp)
    time.sleep(2)
    

    print("Acesso ao busca preço, OK!")
    
    ##Configuração padrão
    print("Iniciando configuração padrão.")
    
    
    
    #clicar em Audio
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[3]").click()
    time.sleep(2)
    
    #Ativa o audio e da OK
                                        
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/fieldset/label[2]/input").click()
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/button").click()
    time.sleep(2)
    

    #clicar em Rede
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[6]").click()
    # alterar ip servidor para o ip da maquina atual
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset[2]/p[1]/input")
    elem.click()
    elem.clear()
    elem.send_keys(ip_local)

    # mascara de rede
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset[2]/p[4]/input")
    elem.click()
    elem.clear()
    elem.send_keys(ip_local)
    

    # Alterar Porta  
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset[2]/p[6]/input")
    elem.click()
    elem.clear()
    elem.send_keys(porta)
    time.sleep(2)

    ##Confirma
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/button").click()
    time.sleep(2)
    
    #clica na aba Wifi
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[7]").click()
    #
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/p[1]/input")
    elem.click()
    elem.clear()
    elem.send_keys(ssid)
    # elem.send_keys(config['SSID'])
    time.sleep(2)
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/p[2]/input[2]").click()
    time.sleep(2)
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/fieldset/p[2]/input[1]")
    elem.click()
    #elem.send_keys(senha_wifi)
    senha= list(senha_wifi)
    #senha= list(config["SENHA_WIFI"])
    
    if elem is not None:
        elem.clear()  # Limpa o campo de input
        elem.send_keys(senha)
    else:
        print("Elemento não encontrado.")
    #print(elem.send_keys(config['SENHA_WIFI']))
  #  print(config['SENHA_WIFI'])
    elem = driver.find_element("xpath", "/html/body/table/tbody/tr[2]/td/form/button").click()
    time.sleep(2)

    #Salva todas as configuracoes /html/body/table/tbody/tr[1]/td/a[10]
    try:
        elem = driver.find_element("xpath", "/html/body/table/tbody/tr[1]/td/a[10]").click()
        time.sleep(2)
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(1)
    except NoAlertPresentException:
        print("Nenhum alerta encontrado.")
    except Exception as e:
        print(f"Erro: {str(e)}")
    print("Audio ativado, OK!")
    print("OK, tudo finalizado!")
    driver.quit()

