import threading
import cv2
import pytesseract
import time

class VisaoComputacional:
    def __init__(self):
        self.cameras = {}
        self.janelas_abertas={}
        self.executar_visualizacoes = True
        self.threads = []

    def iniciar_camera(self, camera_id):
        camera = cv2.VideoCapture(camera_id)
        config = '--oem 3 --psm 6' 
        if not camera.isOpened():
            raise ValueError(f"Não foi possível abrir a câmera {camera_id}")

        self.cameras[camera_id] = camera, config

    def exibir_visualizacao(self, camera_id):
        camera, config = self.cameras.get(camera_id)
        if camera is None:
            raise ValueError(f"A câmera {camera_id} não foi inicializada")
        self.janelas_abertas[camera_id] = f"CAMERA DE NUMERO {camera_id}"
        while self.executar_visualizacoes:
            ret, frame = camera.read()
            if not ret:
                break

            cv2.imshow(f"CAMERA DE NUMERO {camera_id}", frame)
            

            # Pressione a tecla 'q' para sair do loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Após o loop, liberar a câmera e fechar a janela
        #camera.release()
        cv2.destroyAllWindows()

    def exibir_visualizacoes(self):
        #threads = []
        for camera_id in self.cameras:
            thread = threading.Thread(target=self.exibir_visualizacao, args=(camera_id,))
            thread.start()
            self.threads.append(thread)

        # Aguardar até que todas as threads terminem
        for thread in self.threads:
            thread.join()
    
    def fechar_visualizacoes(self, camera_id=None):
        if camera_id is None:
            self.executar_visualizacoes = False  # Define a variável de controle para encerrar as threads

            # Aguardar até que todas as threads terminem
            for thread in self.threads:
                thread.join()

            # Feche todas as janelas registradas no dicionário de janelas abertas
            for camera_id, janela in self.janelas_abertas.items():
                cv2.destroyWindow(janela)

            # Limpe o dicionário de janelas abertas após fechar todas as janelas
            self.janelas_abertas.clear()
        else:
            janela = self.janelas_abertas.get(camera_id)
            if janela is not None:
                cv2.destroyWindow(janela)
                del self.janelas_abertas[camera_id]

    def capturar_texto(self, card):
        if self.camera is None or not self.camera.isOpened():
            raise ValueError("A câmera não foi inicializada")
        else:
            while True:
                ret, frame = self.camera.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                try:
                    text = pytesseract.image_to_string(gray, config=self.config)
                    print(text)

                    formatted_card = str(card).zfill(2)
                    # Exibir o texto extraído
                    cv2.imshow("Texto capturado", gray)
                    cv2.waitKey(1)

                    if f"Disp {formatted_card}" in text:
                        print("Deu certo! Texto capturado!")
                        #retorno = f"Disp {formatted_card}(card)"
                        self.camera.release()  # Liberar a câmera
                        cv2.destroyAllWindows()  # Fechar a janela de visualização
                        return True
                                  
                    else:
                        print(f"Texto não encontrado: {formatted_card}(card)")
                        return False
                except pytesseract.TesseractNotFoundError:
                    print("Não foi possível reconhecer o texto")
                    self.camera.release()  # Liberar a câmera
                    cv2.destroyAllWindows()  # Fechar a janela de visualização
                    return False
                except pytesseract.TesseractError as error:
                    print("Ocorreu um erro durante a requisição ao serviço de reconhecimento de fala:", str(error))
                    self.camera.release()  # Liberar a câmera
                    cv2.destroyAllWindows()  # Fechar a janela de visualização
                    return False

    time_atual = time.time()
    if time_atual - 0 >= 30:
        break

            self.camera.release()  # Liberar a câmera (caso o texto não seja encontrado no tempo limite)
            cv2.destroyAllWindows()  # Fechar a janela de visualização
            return False

    def parar_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

    def listar_cameras(self):
        lista_cameras = []
        num_camera = 0

        while True:
            cap = cv2.VideoCapture(num_camera)
            if not cap.isOpened():
                break

            _, _ = cap.read()
            lista_cameras.append(num_camera)
            cap.release()
            num_camera += 1

        lista_cameras = lista_cameras[:-1]
        return lista_cameras




import threading
import cv2
import pytesseract
import time

class VisaoComputacional:
    def __init__(self):
        self.camera = None

    def exibir_visualizacao(self, camera_id):
        self.camera = cv2.VideoCapture(camera_id)
        self.config = '--oem 3 --psm 6' 
        if not self.camera.isOpened():
            raise ValueError("Não foi possível abrir a câmera")

        while True:
            ret, frame = self.camera.read()
            if not ret:
                break

            cv2.imshow("Visualização da Câmera " + str(camera_id), frame)

            # Pressione a tecla 'q' para sair do loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Após o loop, liberar a câmera e fechar a janela
        self.camera.release()
        cv2.destroyAllWindows()

    def iniciar_camera(self, camera_id):
        thread = threading.Thread(target=self.exibir_visualizacao, args=(camera_id,))
        thread.start()

    def capturar_texto(self, camera_id):
        if not self.camera.isOpened():
            raise ValueError(f"A câmera {camera_id} não foi inicializada")

        resultados = []

        try:
            tempo_inicial = time.time()
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray, config=self.config)
                print(text)

                formatted_card = str(camera_id).zfill(2)

                if f"Disp {formatted_card}" in text:
                    print(f"Deu certo! Texto capturado! Disp {formatted_card}")
                    resultados.append(f"Disp {formatted_card}")

                cv2.imshow("Texto capturado", gray)
                cv2.waitKey(1)

                tempo_atual = time.time()
                if tempo_atual - tempo_inicial >= 30:
                    break
        finally:
            self.camera.release()
            cv2.destroyAllWindows()

        return resultados

    def parar_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

    def listar_cameras(self):
        lista_cameras = []
        num_camera = 0

        while True:
            cap = cv2.VideoCapture(num_camera)
            if not cap.isOpened():
                break

            _, _ = cap.read()
            lista_cameras.append(num_camera)
            cap.release()
            num_camera += 1

        lista_cameras = lista_cameras[:-1]
        return lista_cameras


#@app.route('/iniciar_camera/<int:camera_id>', methods=['GET'])
#def iniciar_camera(camera_id):
    try:
        visao_comp.iniciar_camera(camera_id)
        #visao_comp.exibir_visualizacao(camera_id)
        return jsonify({"status": "Câmera iniciada com sucesso."})
    except ValueError as e:
        return jsonify({"status": str(e)})

@app.route('/capturar_texto/<ip_address>/<int:card>', methods=['GET'])
def capturar_texto(ip_address, card):
    try:
        dispositivo = visao_comp.capturar_texto(card)  # Tempo de 5 segundos para captura do texto
        if dispositivo:
            return "true", 200
        else:
            return "false", 200
    except Exception as e:
        return "false", 500
    
@app.route("/enviar_comando_mesg/<ip_address>/<int:card>", methods=["GET"])
def enviar_comando_mesg(ip_address, card):
#    print(server_obj.terminals)
#    server_obj.remove_disconnected_terminals()
#    print("APOS REMOVE:", server_obj.terminals)
    if server_obj.terminals:
        for terminal in server_obj.terminals.values():
            if terminal.client_address[0] == ip_address:
                try:
                    server_obj.enviar_comando_mesg(terminal, card)
                except Exception as e:
                    return jsonify({"status": str(e)})
                return jsonify({"status": "Comando enviado para o terminal."})

        return jsonify({"status": "IP não encontrado."})
    else:
        return jsonify({"status": "Nenhum terminal conectado."})