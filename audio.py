import time

import speech_recognition as sr


class RecAudio:

    def getTextFromMicrophone(disp: str, tempo: int) -> bool:
        rec = sr.Recognizer()
        mic = sr.Microphone(0)
        time_inicial = time.time()
        is_invalid = False

        with sr.Microphone() as mic:
            while True:
                rec.adjust_for_ambient_noise(mic)
                print("Nesse período o microfone vai ouvir.")
                audio = rec.listen(mic)

                try:
                    texto = rec.recognize_google(audio, language="pt-BR")
                    print(texto)
                    if disp in texto.lower():
                        print(texto)
                        print("Deu certo! O áudio bateu!")
                        return True
                    else:
                        print("audio incoerente!")
                        is_invalid = True
                except sr.UnknownValueError:
                    print("Não foi possível reconhecer o áudio.")
                    return False
                except sr.RequestError as e:
                    print("Ocorreu um erro durante a requisição ao serviço de reconhecimento de fala:", str(e))
                    return False

                time_atual = time.time()
                if time_atual - time_inicial >= tempo:
                    break
                time.sleep(0.1)
            if is_invalid: return False

   