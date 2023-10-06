import threading
import cv2
import pytesseract
import time
from pyzbar import pyzbar

class VisaoComputacional:
    def __init__(self):
        self.camera = None

    def capturar_texto(self, camera_id):
        #camera = cv2.VideoCapture(int(camera_id), cv2.CAP_DSHOW) #COMANDO DA ERRO POR CONTA DA INCREMENTACAO DOS IDS
        camera = cv2.VideoCapture(int(camera_id))
        config = '--oem 3 --psm 6' 
        if not camera.isOpened():
            raise ValueError(f"A câmera {camera_id} não foi inicializada")

        tempo_inicial = time.time()
        tempo_limite = 30  # Defina o tempo limite em segundos

        while True:
            ret, frame = camera.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray, config=config)
            print(text)

            cv2.imshow("Texto capturado", gray)
            cv2.waitKey(1)
            formatted_card = str(camera_id+1).zfill(2) 
            if f"Disp {formatted_card}" in text:
                print("Deu certo! Texto capturado!")
                camera.release()  # Liberar a câmera
                cv2.destroyAllWindows()  # Fechar a janela de visualização
                return True

            tempo_atual = time.time()
            if tempo_atual - tempo_inicial >= tempo_limite:
                break

        camera.release()  # Liberar a câmera (caso o texto não seja encontrado no tempo limite)
        cv2.destroyAllWindows()  # Fechar a janela de visualização
        return False

    def read_qrcode_bancada(self, indice):
        # Inicializa a captura de vídeo
        cap = cv2.VideoCapture(int(indice), cv2.CAP_DSHOW)
        x = 0
        valores = "open"
        time_incial = time.time()
        while True:
            # Lê um frame da câmera
            ret, frame = cap.read()

            # Converte o frame para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detecta os códigos de barra e QR codes no frame
            barcodes = pyzbar.decode(gray)

            time_atual = time.time()
            time_decorrido = time_atual - time_incial
            print(f"RESTAM {time_decorrido} SEGUNDOS")
            if time_decorrido >= 10:
                x = 2
                break

            # Itera sobre os códigos detectados
            for barcode in barcodes:
                # Extrai as coordenadas dos vértices do QR code
                (x, y, w, h) = barcode.rect

                # Desenha um retângulo ao redor do QR code
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Decodifica o conteúdo do QR code
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                print("aqui")

                # Exibe o conteúdo e o tipo do código
                text = "{} ({})".format(barcode_data, barcode_type)
                cv2.putText(frame, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Imprime o conteúdo do QR code
                print("QR Code detectado:", barcode_data)

                if "GERTEC" in barcode_data:
                    x = 1
                    break

                if "disp1" in barcode_data:
                    x = 10
                    valores = barcode_data

                if "disp2" in barcode_data:
                    x = 20
                    valores = barcode_data

                if "disp3" in barcode_data:
                    x = 30
                    valores = barcode_data

            # Exibe o frame
            cv2.imshow("Camera", frame)
            if x == 1:
                return "true"
                break

            if x == 2:
                return "false"
                break

            if x == 10:
                return valores
                break
            if x == 20:
                return valores
                break
            if x == 30:
                return valores
                break

            # Verifica se a tecla 'q' foi pressionada para sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Libera os recursos
        cap.release()
        cv2.destroyAllWindows()

    def listar_cameras(self):
        lista_cameras = []
        num_camera = 0

        while True:
            cap = cv2.VideoCapture(num_camera, cv2.CAP_DSHOW)
            if not cap.isOpened():
                break

            _, _ = cap.read()
            lista_cameras.append(num_camera)
            cap.release()
            num_camera += 1
            #lista_cameras = lista_cameras[:-1]
        return lista_cameras

   