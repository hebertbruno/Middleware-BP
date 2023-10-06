import cv2
import pytesseract
import time


def getTextFromCam(disp: str, tempo: int) -> bool:
    camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    time_inicial = time.time()
    config = '--oem 3 --psm 6'  # Configurações adicionais (opcional)

    while True:
        print("Capturando frame")
        ret, frame = camera.read()

        # Converter o frame para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        try:
            # Realizar OCR na imagem em escala de cinza
            text = pytesseract.image_to_string(gray, config=config)
            print(text)

            # Exibir o texto extraído
            cv2.imshow("Texto capturado", gray)
            cv2.waitKey(1)

            if disp in text:
                print("Deu certo! Texto capturado!")
                camera.release()  # Liberar a câmera
                cv2.destroyAllWindows()  # Fechar a janela de visualização
                return True
            else:
                print("Texto não encontrado")

        except pytesseract.TesseractNotFoundError:
            print("Não foi possível reconhecer o texto")
            camera.release()  # Liberar a câmera
            cv2.destroyAllWindows()  # Fechar a janela de visualização
            return False
        except pytesseract.TesseractError as error:
            print("Ocorreu um erro durante a requisição ao serviço de reconhecimento de fala:", str(error))
            camera.release()  # Liberar a câmera
            cv2.destroyAllWindows()  # Fechar a janela de visualização
            return False

        time_atual = time.time()
        if time_atual - time_inicial >= tempo:
            break

    camera.release()  # Liberar a câmera (caso o texto não seja encontrado no tempo limite)
    cv2.destroyAllWindows()  # Fechar a janela de visualização
    return False


# Chamar a função para iniciar a captura de texto da câmera
resultado = getTextFromCam("192.168.4.117", 30)
print(resultado)