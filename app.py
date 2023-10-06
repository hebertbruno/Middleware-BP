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
visao_comp = VisaoComputacional()
microfone_comp = RecAudio()

# Variaveis de configuracao dos servidores
server_disp1 = Server(server_port=6500)
server_disp2 = Server(server_port=6600)
server_disp3 = Server(server_port=6700)

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
       

## Rota para receber o ssid e Senha e salvar em um JSON
@app.route("/bpg2e_config_wifi", methods=["POST"])
def config_wifi():
    try:
        caminho_json = r"bpg2e_config_wifi.json"
        if not os.path.exists(caminho_json):
            with open(caminho_json, "w") as arquivo:
                config_inicial = {
                    'ssid': '',
                    'senha_wifi': ''
                }
                json.dump(config_inicial, arquivo, indent=4)

        data = request.json
        if not data:
            return print({"error": "Dados inválidos"}), 400
        ssid = data.get('ssid')
        senha_wifi = data.get('senha_wifi')
        if not ssid or not senha_wifi:
            return jsonify({"error": "Parâmetros 'ssid' e 'senha_wifi' são obrigatórios"}), 400
        config = {

            'ssid': ssid,   
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
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    card = str(request.args.get('card_name', default=0,type=str))
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


## CONFIGURACAO PARA ATIVAR O AUDIO, INSERIR OS DADOS DE WIFI NO TERMINAL E SELECIONAR A PORTA USADA
@app.route('/bpg2e_config', methods=['GET'])
def bpg2e_config():
    print("Iniciou a rota")
    try:
        print("dentro do try")
        ip_terminal = str(request.args.get('ip_name', default=0, type=str))
        card = str(request.args.get('card_name', default=0,type=str))

        #de acordo com o card, sera passado como parametro a porta que o terminal ira se conectar
        porta = 6500 if card == 'disp1' else (6600 if card == 'disp2' else (6700 if card == 'disp3' else 0))

        ip_local = socket.gethostbyname(socket.gethostname())
        # Le o JSON com as informacoes do ssid e Senha 
        with open('bpg2e_config_wifi.json') as json_file:
            json_content = json_file.read()
            dados = json.loads(json_content)
            ssid = dados['ssid']  
            senha_wifi = dados['senha_wifi'] 
            print("ip do terminal: ", ip_terminal)
            print("IP LOCAL: ", ip_local)
            print("senha do wifi: ", senha_wifi)
            print("ssid: ", ssid)
            print("Porta utilizada: ", porta)
            print("entrando no selenium")
        
        config_term.config_term(ip_terminal,ip_local, ssid, senha_wifi, porta)
        time.sleep(10)
        return "true", 200

    except Exception as e:
        print("o que deu:", e)
        return "false", 200

## ROTA QUE INICIA O SERVIDOR NA PORTA DESIGNADA DE ACORDO COM O CARD
@app.route('/bpg2e_iniciar_servidor', methods=['GET'])
def iniciar_servidor():
    card = str(request.args.get('card_name', default='', type=str))

    # Mapeie o valor de 'card' para o servidor correspondente
    server = None
    if card == "disp1":
        server = server_disp1
    elif card == "disp2":
        server = server_disp2
    elif card == "disp3":
        server = server_disp3

    if server is not None:
        if server.running:
            server.stop()  # Pare o servidor existente
            time.sleep(2)  # Dê algum tempo para o servidor existente encerrar completamente

        server.start()  # Inicie o novo servidor
        #return f'Servidor {card} iniciado/reiniciado com sucesso.'
        return 'true', 200
    else:
        return 'false', 200

   
## ENVIAR O COMANDO ALWAYSLIVE PARA O TERMINAL NAO SE DESCONECTAR
@app.route('/bpg2e_alwayslive', methods=['GET'])
def enviar_comando_alwayslive():
   
    card = str(request.args.get('card_name', default='', type=str))
        
        # Mapeie o valor de 'card' para o servidor correspondente
    server = None
    if card == "disp1":
        server = server_disp1
    elif card == "disp2":
        server = server_disp2
    elif card == "disp3":
        server = server_disp3
        
    if server is not None:
        if server.terminals:
            for terminal in server.terminals.values():
                command = b'#alwayslive'
                terminal.socket.send(command)
                print(f"alwayslive enviado para o terminal {terminal.client_address}")
                return "true", 200  # jsonify({"status": "Comando alwayslive enviado para todos os terminais conectados."})
            else:
                return 'true', 200  # jsonify({"status": "Nenhum terminal conectado."})
        else:
            return "true", 200
    

## ROTA QUE VERIFICA O STATUS DO SERVIDOR SE ESTÁ ON OU OFF/ SERVE DE FLAG PARA QUE O FRONT PROSSIGA
@app.route('/bpg2e_status', methods=['GET'])
def status():
   # time.sleep(20)
   # server_obj.enviar_comando_mesg()
    card = str(request.args.get('card_name', default=0, type=str))

    # Verifica qual servidor está associado ao card_name fornecido
    if card == "disp1":
        server_obj = server_disp1  # Substitua 'server1' pelo objeto do servidor 1
    elif card == "disp2":
        server_obj = server_disp2  # Substitua 'server2' pelo objeto do servidor 2
    elif card == "disp3":
        server_obj = server_disp3  # Substitua 'server3' pelo objeto do servidor 3
    else:
        return "Invalid card_name", 400  # Resposta de erro para card_name inválido
    
    if server_obj.running:
        return "true", 200
    else:
        return "false", 200

## ROTA QUE FAZ A VALIDACAO SE O TERMINAL COM IP REQUISITADO FEZ A LEITURA DE CODIGO DE BARRAS
@app.route('/bpg2e_scanner', methods=['GET'])
def bpg2e_scanner():
    ip = str(request.args.get('ip_name', default=0, type=str))
    card = str(request.args.get('card_name', default='', type=str))
    
    # Verifica qual servidor está associado ao card_name fornecido
    if card == "disp1":
        server_obj = server_disp1  # Substitua 'server1' pelo objeto do servidor 1
    elif card == "disp2":
        server_obj = server_disp2  # Substitua 'server2' pelo objeto do servidor 2
    elif card == "disp3":
        server_obj = server_disp3  # Substitua 'server3' pelo objeto do servidor 3
    
    
    if server_obj.terminals:
            for terminal in server_obj.terminals.values():
                if terminal.client_address[0] == ip:
                    server_obj.enviar_msg_scannner(terminal) 
                    #server_obj.client_addresses=[]
    time.sleep(15) #Tempo para passar o codigo de barras 
    
    client_addresses = server_obj.lista_ips  # Acessa a lista de IPs corretamente
    print(ip, client_addresses)
    if ip in client_addresses:
        print("IP IGUAL")
        return "true", 200
    else:
        print("IP DIFERENTE")
        return "false", 200

 
## ROTA QUE MANDA UMA MENSAGEM PARA O SERVIDOR E A CAMERA LE A MENSAGEM PARA VALIDAR O DISPLAY DO TERMINAL
@app.route('/bpg2e_display', methods=['GET'])
def bpg2e_display():
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    card = str(request.args.get('card_name', default=0, type=str))
    
    print("valor no card:", card)

    # Verifica qual servidor está associado ao card_name fornecido
    if card == 'disp1':
        server_obj = server_disp1  # Substitua 'server1' pelo objeto do servidor 1
    elif card == 'disp2':
        server_obj = server_disp2  # Substitua 'server2' pelo objeto do servidor 2
    elif card == 'disp3':
        server_obj = server_disp3  # Substitua 'server3' pelo objeto do servidor 3
    
    # Abre o JSON com o mapeamento da camera
    with open('bpg2e_config_cam.json') as json_file:
        json_content = json_file.read()
        dados = json.loads(json_content)
        valor = dados[card]
        print('valor:', valor)

    ## Envia para o terminal a mensagem que deve exibir em tela e atraves do codigo de visao, valida o que foi apresentado
    if server_obj.terminals:
        for terminal in server_obj.terminals.values():
            if terminal.client_address[0] == ip_address:
                try:
                    server_obj.enviar_comando_mesg(terminal, card) 
                    dispositivo = visao_comp.capturar_texto(camera_id=valor)
                    if dispositivo:
                        return "true", 200
                    else:
                        return "false", 200
                except Exception as e:
                    return jsonify({"status": str(e)}), 200
                

@app.route('/bpg2e_buzzer', methods=['GET'])
def bpg2e_audio():
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    card = str(request.args.get('card_name', default=0, type=str))

    # Verifica qual servidor está associado ao card_name fornecido
    if card == "disp1":
        server_obj = server_disp1  # Substitua 'server1' pelo objeto do servidor 1
    elif card == "disp2":
        server_obj = server_disp2  # Substitua 'server2' pelo objeto do servidor 2
    elif card == "disp3":
        server_obj = server_disp3  # Substitua 'server3' pelo objeto do servidor 3
    else:
        return "Invalid card_name", 400  # Resposta de erro para card_name inválido
    
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
    card = str(request.args.get('card_name', default=0, type=str))

    # Verifica qual servidor está associado ao card_name fornecido
    if card == "disp1":
        server_obj = server_disp1  # Substitua 'server1' pelo objeto do servidor 1
    elif card == "disp2":
        server_obj = server_disp2  # Substitua 'server2' pelo objeto do servidor 2
    elif card == "disp3":
        server_obj = server_disp3  # Substitua 'server3' pelo objeto do servidor 3
    else:
        return "Invalid card_name", 400  # Resposta de erro para card_name inválido


    # Le o JSON com as informacoes do ssid e Senha 
    with open('bpg2e_config_wifi.json') as json_file:
        json_content = json_file.read()
        dados = json.loads(json_content)
        ssid = dados['ssid']  
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
    ip_address = str(request.args.get('ip_name', default=0, type=str))
    card = str(request.args.get('card_name', default=0, type=str))

    # Verifica qual servidor está associado ao card_name fornecido
    if card == "disp1":
        server_obj = server_disp1  # Substitua 'server_disp1' pelo objeto do servidor 1
    elif card == "disp2":
        server_obj = server_disp2  # Substitua 'server_disp2' pelo objeto do servidor 2
    elif card == "disp3":
        server_obj = server_disp3  # Substitua 'server_disp3' pelo objeto do servidor 3
    else:
        return "Invalid card_name", 400  # Resposta de erro para card_name inválido

    if server_obj.running:
        server_obj.stop()
        reset_terminal.reset_terminal(ip_address)
        return 'Servidor finalizado com sucesso!'
    else:
        return 'O servidor já está parado.'

    
     
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6900)
  


