import threading
import cv2
import pytesseract
import time

class VisaoComputacional:
    def __init__(self):
        self.camera = None

    def exibir_visualizacao(self, camera_id):
        self.camera = cv2.VideoCapture(camera_id)
        self.config =  '--oem 3 --psm 6' 
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
        camera = cv2.VideoCapture(camera_id)
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
