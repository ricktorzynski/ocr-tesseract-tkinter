import tkinter as tk
import string
from PIL import ImageTk, Image
from tkinter import filedialog, messagebox
import time, os, random
import cv2
from pathlib import Path
import numpy as np
import pytesseract as tess
import argparse

class Page(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("OCR Using Tesseract")
        self.shared_data = {
            "fileName": tk.StringVar()
        }
        container=tk.Frame(self)
        container.grid()
        print(cv2.__version__)
        # Title
        self.empty_name=tk.Label(self, text="OCR Using Tesseract - Version 0.5", font=("Arial", 16))
        self.empty_name.grid(row=0, column=0, pady=5, padx=10, sticky="sw")

        # Intro
        self.intro_lbl = tk.Label(self, text="Demonstration of using Python and Pytesseract in a desktop application for OCR.",
                                  font=("Arial", 11), fg="#202020")
        self.intro_lbl.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nw")

        # Select image                          
        self.browse_lbl = tk.Label(self, text="Select Image :", font=("Arial", 10), fg="#202020")
        self.browse_lbl.grid(row=4, column=0, columnspan=3, padx=24, pady=10, sticky="w")

        self.browse_entry=tk.Entry(self, text="", width=30)
        self.browse_entry.grid(row=4, column=0, columnspan=3, padx=120, pady=10, sticky="w")

        self.browse_btn = tk.Button(self, text="     Browse     ", bg="#ffffff", relief="flat", width=10,
                                    command=lambda:self.show_image())
        self.browse_btn.grid(row=4, column=0, padx=310, pady=10, columnspan=3, sticky="w")
        
        # File selection

        self.lbl_filename = tk.Label(self, text="File Name: ", font=("Arial", 10), fg="#202020")
        self.lbl_filename.grid(row=5, column=0, pady=0, padx=10, columnspan=3, sticky="nw")

        self.lbl_filesize = tk.Label(self, text="File Size: ", font=("Arial", 10), fg="#202020")
        self.lbl_filesize.grid(row=6, column=0, pady=0, padx=10, sticky="nw")

        self.text_file_size=tk.StringVar()
        self.lbl_filesize_01 = tk.Label(self, textvariable=self.text_file_size, font=("Arial", 10), fg="#202020")
        self.lbl_filesize_01.grid(row=6, column=0, pady=0, padx=75, columnspan=3, sticky="nw")

        self.label_text_x = tk.StringVar()
        self.lbl_filename_01 = tk.Label(self, textvariable=self.label_text_x, font=("Arial", 10),fg="#202020")
        self.lbl_filename_01.grid(row=5, column=0, pady=0, padx=85, columnspan=3, sticky="nw")

        # place holder for document thumbnail
        self.lbl_image = tk.Label(self, image="")
        self.lbl_image.grid(row=8, column=0, pady=25, padx=10, columnspan=3, sticky="nw")
        
        # scan button
        self.scan_btn = tk.Button(self, text="      Scan      ", bg="#ffffff", relief="flat",
                                  width=10, command=lambda:self.ocr())

        # save ocr text button
        self.save_btn = tk.Button(self, text="      Save      ", bg="#ffffff", relief="flat",
                                  width=10, command="")
        # text area to place text
        self.ocr_text = tk.Text(self, height=25, width=38)
        
        
        
        # spacer
        self.empty_01 = tk.Label(self, text="")
        self.empty_01.grid(row=29, column=0, columnspan=3, sticky="nsew", pady=152)

    
    def show_image(self):
        global path
        
        # open file dialog
        self.path = filedialog.askopenfilename(defaultextension="*.png", filetypes = (("PNG","*.png"),("JPG", "*.jpg")))
        self.browse_entry.delete(0, tk.END)
        self.browse_entry.insert(0, self.path)

        cv_img = cv2.cvtColor(cv2.imread(self.path), cv2.COLOR_BGR2RGB)
        height, width, no_channels = cv_img.shape

        # resize image
        HEIGHT = 400
      
        imgScale = HEIGHT/height
        newX, newY = cv_img.shape[1]*imgScale, cv_img.shape[0]*imgScale
        newimg = cv2.resize(cv_img, (int(newX), int(newY)))
        photo = ImageTk.PhotoImage(image = Image.fromarray(newimg))
        
        
        
        #photo=ImageTk.PhotoImage(file=self.path)
        self.lbl_image.configure(image=photo)
        self.lbl_image.image=photo

        scan_btn_mid = int(newX/2) - 30;
        self.scan_btn.grid(row=18, column=0, padx=scan_btn_mid, pady=0, columnspan=3, sticky="w")

        self.ocr_text.grid(row=8, column=0, padx=350, pady=26, columnspan=3, sticky="w")
        
        # set the filename
        self.label_text_x.set(os.path.basename(self.path))
        # set the filesize
        self.text_file_size.set(os.path.getsize(self.path))
        

    def ocr(self):

        # load the example image and convert it to grayscale
        self.ocr_image = cv2.imread(self.path)
        gray = cv2.cvtColor(self.ocr_image, cv2.COLOR_BGR2GRAY)
      
        # apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # apply median blurring to remove any blurring
        gray = cv2.medianBlur(gray, 3)

        # save the processed image in the /static/uploads directory
        ofilename = os.path.join('./scans',"{}.png".format(os.getpid()))
        cv2.imwrite(ofilename, gray)


        corrected_img = cv2.cvtColor(cv2.imread(ofilename), cv2.COLOR_BGR2RGB)
        cheight, cwidth, cno_channels = corrected_img.shape

        # resize image
        HEIGHT = 400
        
        cimgScale = HEIGHT/cheight
        cnewX, cnewY = corrected_img.shape[1]*cimgScale, corrected_img.shape[0]*cimgScale
        cnewimg = cv2.resize(corrected_img, (int(cnewX), int(cnewY)))
        cphoto = ImageTk.PhotoImage(image = Image.fromarray(cnewimg))
        
        #photo=ImageTk.PhotoImage(file=self.path)
        self.lbl_image.configure(image=cphoto)
        self.lbl_image.image=cphoto
      
        # perform OCR on the processed image
        text = tess.image_to_string(Image.open(ofilename))
      
        



        


       

if __name__ == "__main__":
    app = Page()
    app.geometry("700x725+100+100")
    app.mainloop()

        
                                 
