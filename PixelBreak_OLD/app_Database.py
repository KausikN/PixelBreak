'''
Summary
This script acts as the frontend to app
'''

import ImageDatabase

import os
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog

curRow = 0
MainLabelText_DB = None
NFilesLabelText_DB = None
FileLabels_DB = []
C_JSON_Text = None
G_JSON_Text = None

C_JSON_Path = ''
G_JSON_Path = ''


# Utils


# TKinter Window
def CreateWindow():
    global curRow
    global MainLabelText_DB
    global NFilesLabelText_DB
    global C_JSON_Text
    global G_JSON_Text

    Button(root, text="Select Dir", command=SelectFileDialogBox_DB).grid(row=curRow, column=0)
    Button(root, text="Add to Database", command=Add2DB).grid(row=curRow, column=1)
    Button(root, text="Remove Last Dir", command=RemoveLastFile_DB).grid(row=curRow, column=2)
    curRow += 1
    Button(root, text="Select Color JSON", command=SelectFileDialogBox_C_JSON).grid(row=curRow, column=0)
    Button(root, text="Select Gray JSON", command=SelectFileDialogBox_G_JSON).grid(row=curRow, column=1)
    curRow += 1
    MainLabelText_DB = tk.StringVar()
    MainLabelText_DB.set("")
    MainLabel_DB = Label(root, textvariable=MainLabelText_DB)
    MainLabel_DB.grid(row=curRow, column=0)
    curRow += 1
    NFilesLabelText_DB = tk.StringVar()
    NFilesLabelText_DB.set("No Files Added")
    NFilesLabel_DB = Label(root, textvariable=NFilesLabelText_DB)
    NFilesLabel_DB.grid(row=curRow, column=0)
    curRow += 1
    C_JSON_Text = tk.StringVar()
    C_JSON_Text.set("No Files Added")
    C_JSON_Label = Label(root, textvariable=C_JSON_Text)
    C_JSON_Label.grid(row=curRow, column=0)
    curRow += 1
    G_JSON_Text = tk.StringVar()
    G_JSON_Text.set("No Files Added")
    G_JSON_Label = Label(root, textvariable=G_JSON_Text)
    G_JSON_Label.grid(row=curRow, column=0)
    curRow += 1

def SelectFileDialogBox_DB():
    global curRow
    global FileLabels_DB
    global MainLabelText_DB
    global NFilesLabelText_DB
    global OpenedDirs

    # Create File Dialog Box
    root.directoryname = filedialog.askdirectory(initialdir='./', title="Select Directory")

    MainLabelText_DB.set("")

    if not root.directoryname in OpenedDirs:
        OpenedDirs.append(root.directoryname)
        NFilesLabelText_DB.set("Added " + str(len(OpenedDirs)) + " Directories")
        newfilelabel = Label(root, text=root.directoryname)
        newfilelabel.grid(row=curRow, column=1)
        FileLabels_DB.append(newfilelabel)
        curRow += 1
    else:
        MainLabelText_DB.set("Dir already added.")

def SelectFileDialogBox_C_JSON():
    global curRow
    global C_JSON_Path
    global C_JSON_Text
    global MainLabelText_DB

    # Create File Dialog Box
    root.filename = filedialog.askopenfilename(initialdir='./', title="Select Color JSON File")

    MainLabelText_DB.set("")

    if not os.path.splitext(root.filename)[-1] == '.json': # Check if selected file is json
        MainLabelText_DB.set("Please select a proper JSON File.")
        return
    else:
        C_JSON_Text.set('Color JSON: ' + root.filename)
        C_JSON_Path = root.filename

def SelectFileDialogBox_G_JSON():
    global curRow
    global G_JSON_Path
    global G_JSON_Text
    global MainLabelText_DB

    # Create File Dialog Box
    root.filename = filedialog.askopenfilename(initialdir='./', title="Select Grayscale JSON File")

    MainLabelText_DB.set("")

    if not os.path.splitext(root.filename)[-1] == '.json': # Check if selected file is json
        MainLabelText_DB.set("Please select a proper JSON File.")
        return
    else:
        G_JSON_Text.set('Gray JSON: ' + root.filename)
        G_JSON_Path = root.filename



def Add2DB():
    global OpenedDirs
    global C_JSON_Path
    global G_JSON_Path

    if not len(OpenedDirs) == 0:
        MainLabelText_DB.set("Adding Images...")
        match_mode = 'avg'
        roundRange = 10
        ImageDatabase.RefreshDatabase(DatabaseLocations=OpenedDirs, G_JSON=G_JSON_Path, C_JSON=C_JSON_Path, match_mode=match_mode, roundRange=roundRange)
        MainLabelText_DB.set("Finished Adding Images")
    else:
        MainLabelText_DB.set("Please select atleast one valid Image file to upload.")

def RemoveLastFile_DB():
    global OpenedDirs
    global FileLabels_DB
    global NFilesLabelText_DB

    if len(OpenedDirs) > 0:
        OpenedDirs.pop()
        FileLabels_DB[-1].grid_forget()
        FileLabels_DB.pop()
        if len(OpenedDirs) > 0:
            NFilesLabelText_DB.set("Added " + str(len(OpenedDirs)) + " Directories")
        else:
            NFilesLabelText_DB.set("No Dir Added")



# Main Code

# Details
OpenedDirs = []

# Init Root
print('Creating Window...')
root = Tk()
root.title('PixelBreak Database App')

# Create Window
CreateWindow()
print('Created Window')

root.mainloop()