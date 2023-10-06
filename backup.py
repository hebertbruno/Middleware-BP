import multiprocessing
from flask import Flask, jsonify, request
import subprocess
import multiprocessing
import socket
import os
import sys
import threading
import time
from flask_cors import CORS
from server import Server, Terminal ## import do Servidor do buca preco
import BP ## import configuracao do wifi em Selenium
import config_term ## import da configuracao do audio do terminal em Selenium
import reset_terminal ## import da configuracao que restaura padrao de fabrica
from displayTeste import VisaoComputacional ## import arquivo do teste de visao computacional
from audio import RecAudio ## import arquivo do teste de audio
import json

app = Flask(__name__)
CORS(app)
server_obj = Server()
visao_comp = VisaoComputacional()
microfone_comp = RecAudio()

ip_addresses = set()  # Conjunto para armazenar os IPs sem repetição

server_ip = socket.gethostbyname(socket.gethostname())#'192.168.100.144'  # ip do servidor(maquina local) por padrão deve ser 192.168.0.17
server_port = 6500

def handle_connection(client_socket, client_address):
    print("Conexão recebida de", client_address[0])
    ip_addresses.add(client_address[0])
    client_socket.close()

def verificar_conexoes():
    print("Verificar")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_socket.bind((server_ip, server_port))
    server_socket.listen(3)  # Aceita até 5 conexões simultâneas

    print("Aguardando conexões na porta", server_port)

    server_socket.settimeout(5)  # Defina um timeout de 5 segundos para aceitar conexões

    start_time = time.time()

    while time.time() - start_time <= 5:
        try:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_connection, args=(client_socket, client_address)).start()
        except socket.timeout:
            print("Timeout de aceitação de conexões após 5 segundos")
            break

    print("Encerrando programa após 5 segundos")
    server_socket.close()

## ROTA PARA BUSCAR OS IPS DOS TERMINAIS PRONTOS PARA O TESTE
@app.route("/bpg2e_buscar_ip", methods=["GET"])
def buscaIp():
    
        print("Iniciando busca de IPs")
        server_obj.stop()
        print("Servidor finalizado, caso exista um rodando...")
        time.sleep(5)
        verificar_conexoes()
        ip_status_list = list(ip_addresses)
        ip_addresses.clear()
        print("Retornando ip_status_list")
        return jsonify(ip_status_list)
       

## Rota para receber o SSID e Senha e salvar em um JSON
@app.route("/bpg2e_config_wifi", methods=["POST"])
def config_wifi():
    try:
        caminho_json = r"bpg2e_config_wifi.json"
        if not os.path.exists(caminho_json):
            with open(caminho_json, "w") as arquivo:
                config_inicial = {
                    'SSID': '',
                    'senha_wifi': ''
                }
                json.dump(config_inicial, arquivo, indent=4)

        data = request.json
        if not data:
            return print({"error": "Dados inválidos"}), 400
        SSID = data.get('SSID')
        senha_wifi = data.get('senha_wifi')
        if not SSID or not senha_wifi:
            return jsonify({"error": "Parâmetros 'ssid' e 'senha_wifi' são obrigatórios"}), 400
        config = {

            'SSID': SSID,   
            'senha_wifi': senha_wifi
        }
        with open(caminho_json, "w") as arquivo:
            json.dump(config, arquivo, indent=4) 
        return "true", 200

    except:
        return "false", 200
    

## ROTA PARA MAPEAR AS CAMERAS AS BANCADAS
@app.route('/bpg2e_mapear_cameras', methods=['GET'])
def mapear_cameras():
    caminho_json = r"bpg2e_config_cam.json"
    config = {}

    cameras = visao_comp.listar_cameras()
    print(cameras)
    for x in cameras:
        if x != 0:
            bancada = visao_comp.read_qrcode_bancada(indice=cameras[x])
            print(bancada)
            config.update({bancada: cameras[x]})
            print(config)
    json_data = json.dumps(config, indent=4)
    with open(caminho_json, "w") as arquivo:
        arquivo.write(json_data)
    print(json_data)
    return "true", 200

## ROTA PARA TESTAR O PING DO IP REQUISITADO
@app.route('/bpg2e_ethernet', methods=["GET"])
def bpg2e_ethernet():
    server_obj.stop()
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    #print(ip)
    ping_path = r'C:\Windows\System32\ping.exe'
    time.sleep(3)
    try:
        output = subprocess.check_output([ping_path, "-n", "1", ip_address]) #alterar para -n no windows e -c no linux
        print("PING success")
        return "true", 200

    except subprocess.CalledProcessError:
        print("Ping failed")
        return "false", 200



## CONFIGURACAO PARA ATIVAR O AUDIO E INSERIR OS DADOS DE WIFI NO TERMINAL
@app.route('/bpg2e_config', methods=['POST'])
def bpg2e_config():
    print("Iniciou a rota")
    try:
        print("dentro do try")
        ip_terminal = str(request.form.get('ip_name', default=0, type=str))
        ip_local = socket.gethostbyname(socket.gethostname())
        # Le o JSON com as informacoes do SSID e Senha 
        with open('bpg2e_config_wifi.json') as json_file:
            json_content = json_file.read()
            dados = json.loads(json_content)
            ssid = dados['SSID']  
            senha_wifi = dados['senha_wifi'] 
            print("ip do terminal: ", ip_terminal)
            print("IP LOCAL: ", ip_local)
            print("senha do wifi: ", senha_wifi)
            print("SSID: ", ssid)
            print("entrando no selenium")
        
        config_term.config_term(ip_terminal,ip_local, ssid, senha_wifi)
        return "true", 200

    except Exception as e:
        print("o que deu:", e)
        return "false", 200

## INICIA O SERVIDOR QUE SE COMUNICARÁ COM O TEMRINAL
@app.route('/bpg2e_iniciar_servidor', methods=['GET'])
def iniciar_servidor():
    
    card = str(request.args.get('card_name', default=0, type=str))
    if card == "disp1":
        print("Req para servidor 01...")
        server_obj.stop()
        time.sleep(7)
        print("Inicializando o servidor 01...")
        server_obj.start()
        return "Servidor iniciado/reiniciado com sucesso.", 200
     
    if card == "disp2":
        print("Req para servidor 02...")
        server_obj.stop()
        time.sleep(7)
        print("Inicializando o servidor 02...")
        server_obj.start()
        return "Servidor iniciado/reiniciado com sucesso.", 200
    
    if card == "disp3":
        print("Req para servidor 03...")
        server_obj.stop()
        time.sleep(7)
        print("Inicializando o servidor 03...")
        server_obj.start()
        return "Servidor iniciado/reiniciado com sucesso.", 200

## ENVIAR O COMANDO ALWAYSLIVE PARA O TERMINAL NAO SE DESCONECTAR
@app.route('/bpg2e_alwayslive', methods=['GET'])
def enviar_comando_alwayslive():


    if server_obj.terminals:
        for terminal in server_obj.terminals.values():
            try:
                command = b'#alwayslive'
                terminal.socket.send(command)
                print("alwayslive enviado para o terminal:", terminal.client_address)
                
            except Exception as e:
                return "false", 200

        return "true", 200 #jsonify({"status": "Comando alwayslive enviado para todos os terminais conectados."})
    else:
        return 'false', 200 #jsonify({"status": "Nenhum terminal conectado."})

## ROTA QUE VERIFICA O STATUS DO SERVIDOR SE ESTÁ ON OU OFF/ SERVE DE FLAG PARA QUE O FRONT PROSSIGA
@app.route('/bpg2e_status', methods=['GET'])
def status():
   # time.sleep(20)
   # server_obj.enviar_comando_mesg()
    if server_obj.running:
        return "true", 200
    else:
        return "false", 200

## ROTA QUE FAZ A VALIDACAO SE O TERMINAL COM IP REQUISITADO FEZ A LEITURA DE CODIGO DE BARRAS
@app.route('/bpg2e_scanner', methods=['GET'])
def bpg2e_scanner():
    ip = str(request.args.get('ip_name', default=0, type=str))
    if server_obj.terminals:
            for terminal in server_obj.terminals.values():
                if terminal.client_address[0] == ip:
                    server_obj.enviar_msg_scannner(terminal) #APENAS PARA MINHA MAQUINA/ USAR card normal
                    #server_obj.client_addresses=[]
    time.sleep(10) #Tempo para passar o codigo de barras 
    
    client_addresses = server_obj.lista_ips  # Acessa a lista de IPs corretamente
    print(ip, client_addresses)
    if ip in client_addresses:
        print("IP IGUAL")
        return "true", 200
    else:
        print("IP DIFERENTE")
        return "false", 200

## ROTA PARA CONFIGURAR OS IPS
@app.route("/bpg2e_config_ips", methods=["POST"])
def config_ips():
    try:
        ip_terminal = str(request.form.get("ip_name", type=str, default=0))
        ip_local = socket.gethostbyname(socket.gethostname())
        print('client_ip:', ip_terminal)
        time.sleep(5)
        print('saiu do sleep')
        #config_term.config_term(ip_terminal, ip_local)
        #requests.get(f"http://{client_ip}:6800/start_firmware")
        #requests.get(f"http://{client_ip}:6800/get_key_press?ip_local={ip_local}&restart_json=false")
        return "true"

    except Exception as e:
        # logging.error(f'ERROR >> ', e)
        return "false", 500
 
## ROTA QUE MANDA UMA MENSAGEM PARA O SERVIDOR E A CAMERA LE A MENSAGEM PARA VALIDAR O DISPLAY DO TERMINAL
@app.route('/bpg2e_display', methods=['GET'])
def bpg2e_display():
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    card = str(request.args.get('card_name', default=0, type=str))

    with open('bpg2e_config_cam.json') as json_file:
        json_content = json_file.read()
        dados = json.loads(json_content)
        valor = dados[card]

    if server_obj.terminals:
        for terminal in server_obj.terminals.values():
            if terminal.client_address[0] == ip_address:
                try:
                    server_obj.enviar_comando_mesg(terminal, card) #APENAS PARA MINHA MAQUINA/ USAR card normal
                    dispositivo = visao_comp.capturar_texto(camera_id=valor)#APENAS PARA MINHA MAQUINA/ USAR card normal
                    if dispositivo:
                        return "true", 200
                    else:
                        return "false", 200
                except Exception as e:
                    return jsonify({"status": str(e)}), 200
                

@app.route('/bpg2e_buzzer', methods=['GET'])
def bpg2e_audio():
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    
    
    if server_obj.terminals:
            for terminal in server_obj.terminals.values():
                if terminal.client_address[0] == ip_address:
                    server_obj.enviar_mensagens(terminal, "Teste o audio")
    
    try:
        fala = "consultando o produto aguarde"
        tempo = 10
        microfone = microfone_comp.getTextFromMicrophone(fala, tempo)
        if microfone:
            return "true", 200
        else:
            return "false", 200
    except:
        return "false", 200
    #if server_obj.terminals:
    #    for terminal in server_obj.terminals.values():
    #        if terminal.client_address[0] == ip_address:
    #            try:
    #                dispositivo = server_obj.enviar_audio(terminal) 
    #                if dispositivo:
    #                    return "true", 200
    #                else:
    #                    return "false", 200
    #            except Exception as e:
    #                return jsonify({"status": str(e)}), 500



## ROTA QUE MUDA A CONFIGURACAO DO TERMINAL PARA WIFI E TESTA O PING        
@app.route('/bpg2e_wifi', methods=['GET'])
def bpg2e_wifi():
    
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    
    # Le o JSON com as informacoes do SSID e Senha 
    with open('bpg2e_config_wifi.json') as json_file:
        json_content = json_file.read()
        dados = json.loads(json_content)
        ssid = dados['SSID']  
        senha_wifi = dados['senha_wifi']  
    
   # Envia para o terminal a mensagem de que esta configurando wifi
    print(ssid, senha_wifi)
    if server_obj.terminals:
            for terminal in server_obj.terminals.values():
                if terminal.client_address[0] == ip_address:
                    server_obj.enviar_mensagens(terminal, "configurando wifi")
    
    
    #realiza a mudanca de ethernet para wifi atraves do Selenium e testa o ping
    ping_path = r'C:\Windows\System32\ping.exe'
    BP.wifi(ip_address)
    time.sleep(17)
    try:
        output = subprocess.check_output([ping_path, "-n", "1", ip_address])
        
        return "true", 200

    except subprocess.CalledProcessError:
        return "false", 200

@app.route('/bpg2e_reset_config', methods=['GET'])
def reset_config():
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    try:
        reset_terminal.reset_terminal(ip_address)
        return 'true', 200
    except:
        return 'false', 200

## ROTA PARA FINALIZAR O SERVIDOR E DESCONECTAR OS TERMINAIS
@app.route('/bpg2e_finalizar_servidor', methods=['GET'])
def finalizar_servidor():
    #if server_obj.terminals:
    #    for terminal in server_obj.terminals.values():
    #        try:
    #            command = b'#checklive'
    #            terminal.socket.send(command)
    #            print("checklive enviado para o terminal:", terminal.client_address)
                
    #        except Exception as e:
    #            print("Erro ao enviar o comando checklive para o terminal:", terminal.client_address)

    try:
        
        server_obj.stop()
        return 'Servidor finalizado com sucesso!'
    except:
        return jsonify({"status": "Nenhum terminal conectado."})
    
     
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
  


