from os import terminal_size
import os
import wave
import signal
import socket
import threading
import time
from pydub import AudioSegment




class Terminal:
    def __init__(self, socket, client_address, server_obj):
        self.socket = socket
        self.client_address = client_address
        self.server_obj = server_obj
        self.on_receive = None
        self.on_disconnect = None
        self.response = None

    def start_receiving(self):
        while True:
            try:
                data = self.socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    if self.on_receive:
                        self.on_receive(self, message)
                else:
                    break
            except ConnectionResetError:
                break
            except OSError as e:
                print(f"Erro na conexão com {self.client_address}: {e}")
                break

        self.disconnect()
        self.server_obj.remove_terminal(self)
        print("Terminal desconectado", self.server_obj)

    def disconnect(self):
        self.socket.close()
        if self.on_disconnect:
            self.on_disconnect(self)


#class Server:
#    client_addresses = []
#    lista_ips = []
#    def __init__(self):
#        self.server_ip = socket.gethostbyname(socket.gethostname()) #alterar o server para 192.168.0.17
#        self.server_port = 6500
#        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self.terminals = {}
#        self.lock = threading.Lock()
#        self.running= True                   
class Server:
    client_addresses = []
    lista_ips = []
    def __init__(self, server_port):
        self.server_ip = socket.gethostbyname(socket.gethostname())
        self.server_port = server_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.terminals = {}
        self.lock = threading.Lock()
        self.running = True   

    def handle_command(self, terminal, command):#funcao para verificar que tipo de requisicao o terminal esta fazendo
        if command.startswith('#bpg2e|4.2.0 S') or command.startswith('#checklive_ok') or command.startswith('#queryprocessfailure') or command.startswith('#mesg_ok') or command.startswith('#alwayslive_ok'):
            pass
        else:
            print(command)
            if terminal.client_address[0] in self.lista_ips:
                self.lista_ips.remove(terminal.client_address[0])
            self.process_barcode(terminal.client_address, command, terminal)
            

    def process_barcode(self, client_address, barcode, terminal):
        
    # Construir o comando de envio
        #self.scanned_barcode = barcode
        product_name = 'SCANNER OK'
        product_price = 'R$ 10.00'
        response = '#' + product_name + '|' + product_price
        terminal.socket.send(response.encode('utf-8'))
        
        print("Print dentro do barcode:", client_address[0])
        self.lista_ips.append(client_address[0])
        #return client_address[0]
       # self.client_addresses.append(client_address[0])  # Adiciona o IP à lista
        #time.sleep(10) #Tempo para zerar a lista de IPs
        

        # Remover o IP da lista após 25 segundos (opcional)
        #3if client_address[0] in self.client_addresses:
        #    self.client_addresses.remove(client_address[0])
        #return True
            

    def remove_terminal(self, terminal):
        with self.lock:
            del self.terminals[terminal.client_address]

    
    def enviar_audio(self, terminal):
        try:
            audio = AudioSegment.from_file('output.wav', format='wav')
            
            volume = 2
            duracao_audio_segundos = 5
            
            tamanho_audi_hex = hex(len(audio))[2:].zfill(12)
            duracao_audio_hex = hex(duracao_audio_segundos)[2:].zfill(8)
            volume_hex = hex(volume)[2:]
            
            dados = tamanho_audi_hex + duracao_audio_hex + volume_hex

            command = "#playaudiowithmessage" + dados 
            terminal.socket.send(command.encode())  # Codifica a string antes de enviar

            # Obter os bytes brutos do áudio
            raw_audio_data = audio.raw_data

            terminal.socket.send(raw_audio_data)
            return True
        except:
            return False

    def enviar_mensagens(self, terminal, mensagem):
        
        partes = mensagem.split(" ", 1)
        Linha1 = partes[0]
        Linha2 = partes[1]
        
        tempo = 8
        reservado = 48  # byte reservado

        # Para definir os tamanhos que precisam ser passados para o protocolo, deve-se adicionar 48 (ou 0x30 em hexa) nos tamanhos das strings
        tamTLinha1 = chr(len(Linha1) + 48)
        tamTLinha2 = chr(len(Linha2) + 48)

        # Variável que guardará todas as informações que serão enviadas
        str_data = f"#mesg{tamTLinha1}{Linha1}{tamTLinha2}{Linha2}{chr(tempo + 48)}{chr(reservado + 48)}"
        comando = str_data.encode('ascii')  # Transforma a string em bytes

        # Envie o comando para o cliente
        print("mensagem enviada para terminal")
        terminal.socket.send(comando)
    
    def enviar_msg_scannner(self, terminal):
        
        
        Linha1 = "Teste o"
        Linha2 = "Scanner"
        
        
        tempo = 8
        reservado = 48  # byte reservado

        # Para definir os tamanhos que precisam ser passados para o protocolo, deve-se adicionar 48 (ou 0x30 em hexa) nos tamanhos das strings
        tamTLinha1 = chr(len(Linha1) + 48)
        tamTLinha2 = chr(len(Linha2) + 48)

        # Variável que guardará todas as informações que serão enviadas
        str_data = f"#mesg{tamTLinha1}{Linha1}{tamTLinha2}{Linha2}{chr(tempo + 48)}{chr(reservado + 48)}"
        comando = str_data.encode('ascii')  # Transforma a string em bytes

        # Envie o comando para o cliente
        print("mensagem enviada para terminal")
        terminal.socket.send(comando)

    def enviar_comando_mesg(self, terminal, card):
        
        if card == 1:
            Linha1 = "Disp 01"
            Linha2 = "Disp 01"
        if card == 2:
            Linha1 = "Disp 02"
            Linha2 = "Disp 02"
        if card == 3:
            Linha1 = "Disp 03"
            Linha2 = "Disp 03"            
       
        tempo = 50
        reservado = 48  # byte reservado

        # Para definir os tamanhos que precisam ser passados para o protocolo, deve-se adicionar 48 (ou 0x30 em hexa) nos tamanhos das strings
        tamTLinha1 = chr(len(Linha1) + 48)
        tamTLinha2 = chr(len(Linha2) + 48)

        # Variável que guardará todas as informações que serão enviadas
        str_data = f"#mesg{tamTLinha1}{Linha1}{tamTLinha2}{Linha2}{chr(tempo + 48)}{chr(reservado + 48)}"
        comando = str_data.encode('ascii')  # Transforma a string em bytes

        # Envie o comando para o cliente
        print("mensagem enviada para terminal")
        terminal.socket.send(comando)
        
    def send_alwayslive_command(self, terminal):
       command = b'#alwayslive'
       terminal.socket.send(command)
    
    def send_ok_command(self, terminal):
        command = b'#ok'
        terminal.socket.send(command)
        
   

    def send_checklife_command(self,terminal):
        print("entrou no check live")
        command = b'#checklife'
        terminal.socket.send(command)
    
   
    
    def start(self):
            self.running = True
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind((self.server_ip, self.server_port))
                self.server.listen(5)
                print('Aguardando conexões na porta:', self.server_port)

                while self.running:
                    #self.remove_disconnected_terminals()
                    client_socket, client_address = self.server.accept()
                    print('Conexão recebida de:', client_address, "na porta:", self.server_port)
                    
                    with self.lock:
                        if client_address not in self.terminals:
                            terminal = Terminal(client_socket, client_address,self)
                            
                        # terminal.on_disconnect = self.remove_terminal
                            self.terminals[client_address] = terminal
                            self.send_ok_command(terminal)
                            terminal.on_receive = self.handle_command
                            #self.send_alwayslive_command(terminal)
                            terminal.on_receive = self.handle_command
                                    
                           
                        else:
                            #self.enviar_comando_mesg(terminal)
                            print("terminal ja conectado...")
                            

                    terminal = self.terminals[client_address]
                    thread = threading.Thread(target=terminal.start_receiving)
                    thread.start()
                self.send_checklive_command(terminal)
                # Envie o comando '#alwayslive' para o terminal
                    #self.send_alwayslive_command(terminal)
                    
                    
                    # Trate a conexão aqui
            except OSError as e:
                print(f"Erro ao vincular o servidor ao endereço {self.server_ip}:{self.server_port}: {e}")
                # Trate o erro de acordo com a sua necessidade
            finally:
                if self.server:
                    self.server.close()

              

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                if self.server:
                    self.server.close()
                    self.server = None
                    print(f'Servidor encerrado na porta {self.server_port}')
                # Faça qualquer limpeza ou encerramento necessário aqui

   

    def remove_terminal(self, terminal):
        with self.lock:
            del self.terminals[terminal.client_address]

#if __name__ == '__main__':
#    server = Server()
#    server.start()

if __name__ == '__main__':
    server_disp1 = Server(server_port=6500)
    server_disp2 = Server(server_port=6600)
    server_disp3 = Server(server_port=6700)

    # Inicie os servidores em threads separadas
    thread_disp1 = threading.Thread(target=server_disp1.start)
    thread_disp2 = threading.Thread(target=server_disp2.start)
    thread_disp3 = threading.Thread(target=server_disp3.start)

    thread_disp1.start()
    thread_disp2.start()
    thread_disp3.start()   