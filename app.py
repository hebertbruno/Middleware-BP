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
from server import Server, Terminal
import BP
import config_term
from displayTeste import VisaoComputacional 

app = Flask(__name__)
CORS(app)
server_obj = Server()
visao_comp = VisaoComputacional()

ip_addresses = set()  # Conjunto para armazenar os IPs sem repetição

server_ip = '192.168.4.112'  # ip do servidor(maquina local) por padrão deve ser 192.168.0.17
server_port = 6500

def handle_connection(client_socket, client_address):
    print("Conexão recebida de", client_address[0])
    ip_addresses.add(client_address[0])
    client_socket.close()

def verificar_conexoes():
    print("Verificar")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)  # Aceita até 5 conexões simultâneas

    print("Aguardando conexões na porta", server_port)

    start_time = time.time()

    while time.time() - start_time <= 5:
        try:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_connection, args=(client_socket, client_address)).start()
        except socket.timeout:
            pass

    print("Encerrando programa após 3 segundos")
    server_socket.close()

## ROTA PARA BUSCAR OS IPS DOS TERMINAIS PRONTOS PARA O TESTE
@app.route("/bpg2e_buscar_ip", methods=["GET"])
def buscaIp():
    verificar_conexoes()
    ip_status_list = list(ip_addresses)
    ip_addresses.clear()
    return jsonify(ip_status_list)       

## ROTA PARA TESTAR O PING DO IP REQUISITADO
@app.route('/bpg2e_ethernet/<ip_address>', methods=["GET"])
def bpg2e_ethernet(ip_address):
    ip = ip_address
    ping_path = r'C:\Windows\System32\ping.exe'
    time.sleep(3)
    try:
        output = subprocess.check_output([ping_path, "-n", "1", ip]) #alterar para -n no windows e -c no linux
        print("PING")
        return "true", 200

    except subprocess.CalledProcessError:
        print("Error")
        return "false", 200

## CONFIGURACAO PARA ATIVAR O AUDIO DO BUSCA PRECO
@app.route('/bpg2e_config/<ip_address>', methods=['GET'])
def bpg2e_ativa_audio(ip_address):
    
    config_term.config_term(ip_address)
    try:
        return "true", 200
    except subprocess.CalledProcessError:
        return "false", 200

## INICIA O SERVIDOR QUE SE COMUNICARÁ COM O TEMRINAL
@app.route('/bpg2e_iniciar_servidor', methods=['GET'])
def iniciar_servidor():
    #time.sleep()
    server_obj.start()
    return "true", 200

## ENVIAR O COMANDO ALWAYSLIVE PARA O TERMINAL NAO SE DESCONECTAR
@app.route('/enviar_comando_alwayslive', methods=['GET'])
def enviar_comando_alwayslive():
    if server_obj.terminals:
        for terminal in server_obj.terminals.values():
            try:
                command = b'#alwayslive'
                terminal.socket.send(command)
                print("alwayslive enviado para o terminal:", terminal.client_address)
            except Exception as e:
                return "false", 500

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
@app.route('/bpg2e_scanner/<ip_address>', methods=['GET'])
def bpg2e_scanner(ip_address):
    time.sleep(7) #Tempo para passar o codigo de barras 
    ip = ip_address
    client_addresses = server_obj.client_addresses  # Acessa a lista de IPs corretamente
    print(ip, client_addresses)
    if ip in client_addresses:
        print("IP IGUAL")
        return "true", 200
    else:
        print("IP DIFERENTE")
        return "false", 200


##ROTA PARA LISTAR E INICIAR TODAS AS CAMERAS CONECTADAS
@app.route('/listar_e_iniciar_cameras', methods=['GET'])
def listar_e_iniciar_cameras():
    try:
        cameras_online = visao_comp.listar_cameras()
        if cameras_online:
            for camera_id in cameras_online:
                print(cameras_online)
                visao_comp.iniciar_camera(camera_id)
            return jsonify({"status": "Câmeras iniciadas com sucesso."})
        else:
            return jsonify({"status": "Nenhuma câmera disponível."}), 400
    except Exception as e:
        return jsonify({"status": str(e)}), 500

# 3. Crie uma nova rota para exibir as visualizações das câmeras
@app.route('/exibir_visualizacao/<int:camera_id>', methods=['GET'])
def exibir_visualizacao(camera_id):
    # 4. Chame o método exibir_visualizacoes() da instância de VisaoComputacional
    visao_comp.exibir_visualizacao(camera_id)
    return jsonify({"status": "Visualização das câmeras iniciada."})
 
## ROTA QUE MANDA UMA MENSAGEM PARA O SERVIDOR E A CAMERA LE A MENSAGEM PARA VALIDAR O DISPLAY DO TERMINAL
@app.route('/bpg2e_display/<ip_address>/<int:card>', methods=['GET'])
def bpg2e_display(ip_address, card):
    
    if server_obj.terminals:
        for terminal in server_obj.terminals.values():
            if terminal.client_address[0] == ip_address:
                try:
                    server_obj.enviar_comando_mesg(terminal, card) #APENAS PARA MINHA MAQUINA/ USAR card normal
                    dispositivo = visao_comp.capturar_texto(card-1)#APENAS PARA MINHA MAQUINA/ USAR card normal
                    if dispositivo:
                        return "true", 200
                    else:
                        return "false", 200
                except Exception as e:
                    return jsonify({"status": str(e)}), 500
                

## ROTA QUE MUDA A CONFIGURACAO DO TERMINAL PARA WIFI E TESTA O PING        
@app.route('/bpg2e_wifi/<ip_address>', methods=['GET'])
def bpg2e_wifi(ip_address):
    ip = ip_address
    ping_path = r'C:\Windows\System32\ping.exe'
    BP.wifi(ip_address)
    time.sleep(17)
    try:
        output = subprocess.check_output([ping_path, "-n", "1", ip])
        print(ip)
        return "true", 200

    except subprocess.CalledProcessError:
        return "false", 500

## ROTA PARA FINALIZAR O SERVIDOR E DESCONECTAR OS TERMINAIS
@app.route('/bpg2e_finalizar_servidor', methods=['GET'])
def finalizar_servidor():
    if server_obj.terminals:
        for terminal in server_obj.terminals.values():
            try:
                command = b'#checklive'
                terminal.socket.send(command)
                print("checklive enviado para o terminal:", terminal.client_address)
                
            except Exception as e:
                print("Erro ao enviar o comando checklive para o terminal:", terminal.client_address)

        server_obj.stop()
        return 'Servidor finalizado com sucesso!'
    else:
        return jsonify({"status": "Nenhum terminal conectado."})
    
     
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
  


