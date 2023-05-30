# Importing Libraries

import numpy as np

import cv2
import os, sys
import time
import operator

from string import ascii_uppercase

import tkinter as tk
from PIL import Image, ImageTk

from hunspell import Hunspell
import enchant

from keras.models import model_from_json

os.environ["THEANO_FLAGS"] = "device=cuda, assert_no_cpu_op=True"

class Application:
    def __init__(self):
        self.hs = Hunspell('en_US')
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        self.json_file = open("Models\model_new.json", "r")
        self.model_json = self.json_file.read()
        self.json_file.close()

        self.loaded_model = model_from_json(self.model_json)
        self.loaded_model.load_weights("Models\model_new.h5")

        self.json_file_dru = open("Models\model-bw_dru.json" , "r")
        self.model_json_dru = self.json_file_dru.read()
        self.json_file_dru.close()

        self.loaded_model_dru = model_from_json(self.model_json_dru)
        self.loaded_model_dru.load_weights("Models\model-bw_dru.h5")
        self.json_file_tkdi = open("Models\model-bw_tkdi.json" , "r")
        self.model_json_tkdi = self.json_file_tkdi.read()
        self.json_file_tkdi.close()

        self.loaded_model_tkdi = model_from_json(self.model_json_tkdi)
        self.loaded_model_tkdi.load_weights("Models\model-bw_tkdi.h5")
        self.json_file_smn = open("Models\model-bw_smn.json" , "r")
        self.model_json_smn = self.json_file_smn.read()
        self.json_file_smn.close()

        self.loaded_model_smn = model_from_json(self.model_json_smn)
        self.loaded_model_smn.load_weights("Models\model-bw_smn.h5")

        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0

        for i in ascii_uppercase:
          self.ct[i] = 0
        
        print("Loaded model from disk")

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

        mode_option = tk.IntVar()
        self.rb_mode1 = tk.Radiobutton(self.panel_mode, text = "Palabras", variable = mode_option, value = 1, command = lambda: print(mode_option.get()), indicatoron = False, selectcolor = "#4A569D")
        self.rb_mode2 = tk.Radiobutton(self.panel_mode, text = "Frases", variable = mode_option, value = 2, command = lambda: print(mode_option.get()), indicatoron = False, selectcolor = "#ED4264")
        mode_option.set(1)
        self.rb_mode1.configure(width = 50, compound = 'left', background = "#1F2937", font = ("YouTube-Sans-Bold", 20), foreground = "#DFE4EA")
        self.rb_mode2.configure(width = 50, compound = 'left', background = "#1F2937", font = ("YouTube-Sans-Bold", 20), foreground = "#DFE4EA")
        self.rb_mode1.pack()
        self.rb_mode2.pack()

        self.btn_speak = tk.Button(self.root, text = "Borrar último", command = self.speak, relief = tk.GROOVE)
        self.btn_speak.place(x = 700 - 40, y = 360, width = 165)
        self.btn_speak.configure(background = "#14181D", font = ("YouTube-Sans-Light", 20), foreground = "#DFE4EA", borderwidth = 0)

        self.btn_speak = tk.Button(self.root, text = "Borrar todo", command = self.speak, relief = tk.GROOVE)
        self.btn_speak.place(x = 700 - 40, y = 420, width = 165)
        self.btn_speak.configure(background = "#14181D", font = ("YouTube-Sans-Light", 20), foreground = "#DFE4EA", borderwidth = 0)

        self.btn_speak = tk.Button(self.root, text = "Play", command = self.speak, relief = tk.GROOVE)
        self.btn_speak.place(x = 700 - 40, y = 480, width = 165)
        self.btn_speak.configure(background = "#14181D", font = ("YouTube-Sans-Bold", 20), foreground = "#DFE4EA", borderwidth = 0)

        self.T = tk.Label(self.root)
        self.T.place(x = 60, y = 5)
        self.T.config(text = "Show Me A Mexican Sign", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#DFE4EA", background = "#1F2937")

        self.panel3 = tk.Label(self.root) # Current Character
        self.panel3.place(x = 215, y = 540)

        self.T1 = tk.Label(self.root)
        self.T1.place(x = 60, y = 540)
        self.T1.config(text = "Letra:", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#DFE4EA", background = "#1F2937")

        self.panel4 = tk.Label(self.root) # Word/Expression
        self.panel4.place(x = 210, y = 595)

        self.T2 = tk.Label(self.root)
        self.T2.place(x = 60, y = 595)
        self.T2.config(text = "Palabra:", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#DFE4EA", background = "#1F2937")

        """
        self.panel5 = tk.Label(self.root) # Sentence
        self.panel5.place(x = 350, y = 645)

        self.T3 = tk.Label(self.root)
        self.T3.place(x = 60, y = 645)
        self.T3.config(text = "Oración:", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#DFE4EA", background = "#1F2937")

        self.T4 = tk.Label(self.root)
        self.T4.place(x = 250, y = 690)
        self.T4.config(text = "Sugerencias:", font = ("YouTube-Sans-Bold", 30, "bold"), fg = "#4A569D", background = "#1F2937")

        self.bt1 = tk.Button(self.root, command = self.action1, height = 0, width = 0)
        self.bt1.place(x = 26, y = 745)

        self.bt2 = tk.Button(self.root, command = self.action2, height = 0, width = 0)
        self.bt2.place(x = 325, y = 745)

        self.bt3 = tk.Button(self.root, command = self.action3, height = 0, width = 0)
        self.bt3.place(x = 625, y = 745)
        """

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

            self.panel3.config(text = self.current_symbol, font = ("YouTube-Sans-Bold", 30), fg = "#ED4264", background = "#1F2937")
            self.panel4.config(text = self.word, font = ("YouTube-Sans-Light", 30), fg = "#F0F3F7", background = "#1F2937")
            """
            self.panel5.config(text = self.str,font = ("YouTube-Sans-Light", 30), fg = "#F0F3F7", background = "#1F2937")

            predicts = self.hs.suggest(self.word)
            
            if(len(predicts) > 1):
                self.bt1.config(text = predicts[0], font = ("YouTube Sans Medium", 20))
            else:
                self.bt1.config(text = "")

            if(len(predicts) > 2):
                self.bt2.config(text = predicts[1], font = ("YouTube Sans Medium", 20))
            else:
                self.bt2.config(text = "")

            if(len(predicts) > 3):
                self.bt3.config(text = predicts[2], font = ("YouTube Sans Medium", 20))
            else:
                self.bt3.config(text = "")
            """

        self.root.after(5, self.video_loop)

    def predict(self, test_image):
        test_image = cv2.resize(test_image, (128, 128))

        result = self.loaded_model.predict(test_image.reshape(1, 128, 128, 1))

        result_dru = self.loaded_model_dru.predict(test_image.reshape(1 , 128 , 128 , 1))

        result_tkdi = self.loaded_model_tkdi.predict(test_image.reshape(1 , 128 , 128 , 1))

        result_smn = self.loaded_model_smn.predict(test_image.reshape(1 , 128 , 128 , 1))

        prediction = {}

        prediction['blank'] = result[0][0]

        inde = 1

        for i in ascii_uppercase:
            prediction[i] = result[0][inde]
            inde += 1

        #LAYER 1

        prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)

        self.current_symbol = prediction[0][0]

        #LAYER 2

        if(self.current_symbol == 'D' or self.current_symbol == 'R' or self.current_symbol == 'U'):

        	prediction = {}

        	prediction['D'] = result_dru[0][0]
        	prediction['R'] = result_dru[0][1]
        	prediction['U'] = result_dru[0][2]

        	prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)

        	self.current_symbol = prediction[0][0]

        if(self.current_symbol == 'D' or self.current_symbol == 'I' or self.current_symbol == 'K' or self.current_symbol == 'T'):

        	prediction = {}

        	prediction['D'] = result_tkdi[0][0]
        	prediction['I'] = result_tkdi[0][1]
        	prediction['K'] = result_tkdi[0][2]
        	prediction['T'] = result_tkdi[0][3]

        	prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)

        	self.current_symbol = prediction[0][0]

        if(self.current_symbol == 'M' or self.current_symbol == 'N' or self.current_symbol == 'S'):

        	prediction1 = {}

        	prediction1['M'] = result_smn[0][0]
        	prediction1['N'] = result_smn[0][1]
        	prediction1['S'] = result_smn[0][2]

        	prediction1 = sorted(prediction1.items(), key = operator.itemgetter(1), reverse = True)

        	if(prediction1[0][0] == 'S'):
        		self.current_symbol = prediction1[0][0]
        	else:
        		self.current_symbol = prediction[0][0]
        
        if(self.current_symbol == 'blank'):
            for i in ascii_uppercase:
                self.ct[i] = 0

        self.ct[self.current_symbol] += 1

        if(self.ct[self.current_symbol] > 60):
            for i in ascii_uppercase:
                if i == self.current_symbol:
                    continue

                tmp = self.ct[self.current_symbol] - self.ct[i]

                if tmp < 0:
                    tmp *= -1

                if tmp <= 20:
                    self.ct['blank'] = 0

                    for i in ascii_uppercase:
                        self.ct[i] = 0
                    return

            self.ct['blank'] = 0

            for i in ascii_uppercase:
                self.ct[i] = 0

            if self.current_symbol == 'blank':
                if self.blank_flag == 0:
                    self.blank_flag = 1

                    if len(self.str) > 0:
                        self.str += " "

                    self.str += self.word

                    self.word = ""
            else:
                if(len(self.str) > 16):
                    self.str = ""

                self.blank_flag = 0

                self.word += self.current_symbol

    def speak(self):
         print("")
    """
    def action1(self):
    	predicts = self.hs.suggest(self.word)

    	if(len(predicts) > 0):
            self.word = ""

            self.str += " "

            self.str += predicts[0]

    def action2(self):
    	predicts = self.hs.suggest(self.word)

    	if(len(predicts) > 1):
            self.word = ""
            self.str += " "
            self.str += predicts[1]

    def action3(self):
    	predicts = self.hs.suggest(self.word)

    	if(len(predicts) > 2):
            self.word = ""
            self.str += " "
            self.str += predicts[2]

    def action4(self):
    	predicts = self.hs.suggest(self.word)

    	if(len(predicts) > 3):
            self.word = ""
            self.str += " "
            self.str += predicts[3]

    def action5(self):
    	predicts = self.hs.suggest(self.word)

    	if(len(predicts) > 4):
            self.word = ""
            self.str += " "
            self.str += predicts[4]
    """
            
    def destructor(self):
        print("Closing Application...")

        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()
    
print("Starting Application...")

(Application()).root.mainloop()