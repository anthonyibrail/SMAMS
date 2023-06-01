# Importing Libraries

import numpy as np

import cv2
import os, sys
import time
import operator

from string import ascii_uppercase

import tkinter as tk
from PIL import Image, ImageTk

#from hunspell import Hunspell
#import enchant

from gtts import gTTS
from playsound import playsound

from keras.models import model_from_json

os.environ["THEANO_FLAGS"] = "device=cuda, assert_no_cpu_op=True"

class Application:
    def __init__(self):
        #self.hs = Hunspell('en_US')
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        self.json_file = open("Models\model_new_5.json", "r")
        self.model_json = self.json_file.read()
        self.json_file.close()

        self.loaded_model = model_from_json(self.model_json)
        self.loaded_model.load_weights("Models\model_new_5.h5")

        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0

        self.expressions = {
            "Estrellas brillantes iluminan el espacio.", 
            "Luna, nuestro vecino nocturno.", 
            "Agujeros negros: misterio infinito.",
            "Gravedad distinta, reglas cambian.",
            "Vía Láctea, nuestra galaxia hogar.",
            "Aire ausente, trajes indispensables.",
            "Radiación cósmica, peligro omnipresente.",
            "Telescopios desvelan secretos celestiales.",
            "Silencio absoluto, vacío infinito.",
            "",
            "",
            "Espacio hostil, vida imposible.",
            "Nebulosas: gas y polvo estelar.",
            "Estrellas ardientes, gigantes incandescentes.",
            "Galaxias, sistemas solares interminables.",
            "Sol, estrella radiante y poderosa.",
            "Asombro y maravilla, espacio infinito.",
            "Cometas: viajeros celestiales errantes.",
            "Espacio profundo, territorio inexplorado.",
            "Gravedad cero, flotar en espacio.",
            "Exploración espacial, comprensión universal.",
            "Estrellas fugaces, deseos cumplidos.",
            "Universo vasto, infinitas posibilidades.",
            "Estación Espacial Internacional: laboratorio orbital.",
            "Exploración espacial, progreso científico importante.",
            "Misterio cósmico infinito.",
            ""
        }

        for i in ascii_uppercase:
          self.ct[i] = 0
        
        print("Model loaded")

        self.root = tk.Tk()
        self.root.title("SMAMS")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("845x660")
        self.root.configure(background = "#1F2937")
        self.root.iconbitmap("icon.ico")

        self.panel = tk.Label(self.root) # Camera panel
        self.panel.place(x = 100 - 40, y = 10, width = 580, height = 580)
        self.panel.configure(background = "#1F2937")
        
        self.panel2 = tk.Label(self.root) # ROI area
        self.panel2.place(x = 400 - 40, y = 65, width = 275, height = 275)

        self.T = tk.Label(self.root) # Mode label
        self.T.place(x = 730 - 40, y = 65)
        self.T.config(text = "Modo", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#4A569D", background = "#1F2937")

        self.panel_mode = tk.Label(self.root) # Mode options
        self.panel_mode.place(x = 705 - 40, y = 120, width = 150, height = 100)
        self.panel_mode.configure(background = "#1F2937")

        self.mode_option = tk.IntVar()
        self.rb_mode1 = tk.Radiobutton(self.panel_mode, text = "Palabras", variable = self.mode_option, value = 1, command = self.mode_1, indicatoron = False, selectcolor = "#4A569D")
        self.rb_mode2 = tk.Radiobutton(self.panel_mode, text = "Frases", variable = self.mode_option, value = 2, command = self.mode_2, indicatoron = False, selectcolor = "#ED4264")
        self.mode_option.set(1)
        self.rb_mode1.configure(width = 50, compound = 'left', background = "#1F2937", font = ("YouTube-Sans-Bold", 20), foreground = "#DFE4EA")
        self.rb_mode2.configure(width = 50, compound = 'left', background = "#1F2937", font = ("YouTube-Sans-Bold", 20), foreground = "#DFE4EA")
        self.rb_mode1.pack()
        self.rb_mode2.pack()

        self.btn_add = tk.Button(self.root, text = "Agregar", command = self.add_char, relief = tk.GROOVE)
        self.btn_add.place(x = 700 - 40, y = 300, width = 165)
        self.btn_add.configure(background = "#ED4264", font = ("YouTube-Sans-Bold", 20), foreground = "#DFE4EA", borderwidth = 0)        

        self.btn_dlt_1 = tk.Button(self.root, text = "Borrar último", command = self.cls_last, relief = tk.GROOVE)
        self.btn_dlt_1.place(x = 700 - 40, y = 360, width = 165)
        self.btn_dlt_1.configure(background = "#14181D", font = ("YouTube-Sans-Light", 20), foreground = "#DFE4EA", borderwidth = 0)

        self.btn_dlt_2 = tk.Button(self.root, text = "Borrar todo", command = self.cls_all, relief = tk.GROOVE)
        self.btn_dlt_2.place(x = 700 - 40, y = 420, width = 165)
        self.btn_dlt_2.configure(background = "#14181D", font = ("YouTube-Sans-Light", 20), foreground = "#DFE4EA", borderwidth = 0)

        self.btn_speak = tk.Button(self.root, text = "Play", command = self.player, relief = tk.GROOVE)
        self.btn_speak.place(x = 700 - 40, y = 480, width = 165)
        self.btn_speak.configure(background = "#14181D", font = ("YouTube-Sans-Bold", 20), foreground = "#DFE4EA", borderwidth = 0)

        self.T = tk.Label(self.root)
        self.T.place(x = 60, y = 5)
        self.T.config(text = "Show Me A Mexican Sign", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#DFE4EA", background = "#1F2937")

        self.panel3 = tk.Label(self.root) # Current Character
        self.panel3.place(x = 215, y = 550)

        self.T1 = tk.Label(self.root)
        self.T1.place(x = 60, y = 540)
        self.T1.config(text = "Letra:", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#DFE4EA", background = "#1F2937")

        self.panel4 = tk.Label(self.root) # Word
        self.panel4.place(x = 210, y = 605)

        self.T2 = tk.Label(self.root)
        self.T2.place(x = 60, y = 595)
        self.T2.config(text = "Palabra:", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#DFE4EA", background = "#1F2937")

        self.str = ""
        self.word = " "
        self.current_symbol = "Empty"
        self.photo = "Empty"
        self.video_loop()

    def video_loop(self):
        ok, frame = self.vs.read()

        if ok:
            cv2image = cv2.flip(frame, 1)

            x1 = int(0.5 * frame.shape[1])
            y1 = 10
            x2 = frame.shape[1] - 10
            y2 = int(0.5 * frame.shape[1])

            cv2.rectangle(frame, (x1 - 1, y1 - 1), (x2 + 1, y2 + 1), (255, 0, 0) ,1)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)

            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image = self.current_image)

            self.panel.imgtk = imgtk
            self.panel.config(image = imgtk)

            cv2image = cv2image[y1 : y2, x1 : x2]

            gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)

            blur = cv2.GaussianBlur(gray, (5, 5), 2)

            th3 = cv2.adaptiveThreshold(blur, 255 ,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            self.predict(res)

            self.current_image2 = Image.fromarray(res)

            imgtk = ImageTk.PhotoImage(image = self.current_image2)

            self.panel2.imgtk = imgtk
            self.panel2.config(image = imgtk)

            self.panel3.config(text = self.current_symbol, font = ("YouTube-Sans-Bold", 20), fg = "#ED4264", background = "#1F2937")
            if self.mode_option.get() == 1:
                self.panel4.config(text = self.word, font = ("YouTube-Sans-Light", 20), fg = "#F0F3F7", background = "#1F2937")
            else:
                self.panel4.config(text = self.word, font = ("YouTube-Sans-Light", 20), fg = "#1F2937", background = "#1F2937")
                

        self.root.after(5, self.video_loop)
    
    def predict(self, test_image):
        test_image = cv2.resize(test_image, (128, 128))

        result = self.loaded_model.predict(test_image.reshape(1, 128, 128, 1))

        prediction = {}

        prediction['blank'] = result[0][0]

        inde = 1

        if self.mode_option.get() == 1:
            for i in ascii_uppercase:
                prediction[i] = result[0][inde]
                inde += 1
        else:
            for i in self.expressions:
                prediction[i] = result[0][inde]
                inde += 1

        prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)
        self.current_symbol = prediction[0][0]

    # Callbacks
    def mode_1(self):
        self.mode_option.set(1)
        self.btn_add.configure(state = 'normal')
        self.btn_dlt_1.configure(state = 'normal')
        self.btn_dlt_2.configure(state = 'normal')
        self.T1.configure(text = "Letra:")
        self.T2.configure(fg = "#DFE4EA")
        self.panel4.configure(fg = "#F0F3F7")

    def mode_2(self):
        self.mode_option.set(2)
        self.btn_add.configure(state = 'disabled')
        self.btn_dlt_1.configure(state = 'disabled')
        self.btn_dlt_2.configure(state = 'disabled')
        self.T1.configure(text = "Frase:")
        self.T2.configure(fg = "#1F2937")
        self.panel4.configure(fg = "#1F2937")

    def add_char(self):
        self.word += self.current_symbol

    def cls_last(self):
        try:
            self.word = self.word[0: len(self.word) - 1]
        except: print("")

    def cls_all(self):
        self.word = ""

    def player(self):
        if self.mode_option.get() == 1:
            #if self.word != "":
            try:
                tts = gTTS(text = self.word, lang = 'es')
                tts.save("output.mp3")
                full_path = os.path.abspath("output.mp3")
                time.sleep(1)
                playsound(full_path)
            except: print("")
        else:
            #if self.current_symbol != "":
            try:
                tts = gTTS(text = self.current_symbol , lang = 'es')
                tts.save("output.mp3")
                full_path = os.path.abspath("output.mp3")
                time.sleep(1)
                playsound(full_path)
            except: print("")

    def space(self):
        interrupt = cv2.waitKey(10)
        if interrupt & 0xFF == 32:
            self.word += " "
            
    def destructor(self):
        print("Closing App...")
        try:
            full_path = os.path.abspath("output.mp3")
            os.remove(full_path)
        except: print("")

        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()
    
print("Starting App...")

(Application()).root.mainloop()