'''
Summary
This script is to organise the image database from which fill Images are taken
Add Image
Delete Image
Update FillImgs JSON Files / Refresh Database
Generate Basic FillImages
'''
import cv2
import numpy as np
import random
import json
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

Images = [] # [path, GMatchVal, CMatchVal]

class ImageDetails:
    def __init__(self, path, GMatchVal, CMatchVal):
        self.path = path
        self.GMatchVal = GMatchVal
        self.CMatchVal = CMatchVal

def RefreshDatabase(DatabaseLocations=['FillImgs'], G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json', match_mode='avg', roundRange=10):
    global Images
    Images = []
    #DatabaseLocationProgress = 1
    #TotalLocs = len(DatabaseLocations)
    print("Refreshing File List...")
    for DatabaseLocation in tqdm(DatabaseLocations):
        for dirpath, dirnames, filenames in os.walk(DatabaseLocation):
            for filename in filenames:
                imgd = ImageDetails(os.path.join(dirpath, filename), 0.0, [0.0, 0.0, 0.0])
                Images.append(imgd)
        #print("Hashed", DatabaseLocation, ":", DatabaseLocationProgress, "/", TotalLocs)
        #DatabaseLocationProgress += 1
    UpdateImagesMatchVals(match_mode)
    print("Image Values Updated")
    G_Dict = GenerateGreyScaleDict(roundRange)
    print("GrayScale JSON Dictionary Generated")
    C_Dict = GenerateColorDict(roundRange)
    print("Color JSON Dictionary Generated")
    #print(G_Dict)
    #print(C_Dict)
    UpdateJSONFiles(G_Dict, C_Dict, G_JSON, C_JSON)
    print("JSON Files Updated")

def UpdateImagesMatchVals(match_mode='avg'):
    global Images
    print("Updating Image Match Vals...")
    for i in tqdm(range(len(Images))):
        if match_mode == 'avg':
            I = cv2.imread(Images[i].path)
            I_g = cv2.imread(Images[i].path, 0)
            Images[i].GMatchVal = np.sum(np.sum(I_g, axis=1), axis=0) / (I_g.shape[0]*I_g.shape[1])
            Images[i].CMatchVal = np.sum(np.sum(I, axis=1), axis=0) / (I.shape[0]*I.shape[1])
        elif match_mode == 'name': # Name is of form Type_SubDirName_000_000_000.png for color
            filename = os.path.splitext(os.path.basename(Images[i].path))[0]
            Images[i].CMatchVal = list(map(int, filename[-11:].split('_'))) 
            Images[i].GMatchVal = int(0.2989 * Images[i].CMatchVal[0] + 0.5870 * Images[i].CMatchVal[1] + 0.1140 * Images[i].CMatchVal[2])
    
def GenerateGreyScaleDict(roundRange=200):
    global Images
    G_Dict = {}
    G_Dict['roundrange'] = roundRange
    for i in range(0, 261, roundRange):
        G_Dict[str(i)] = []
    for img in Images:
        ValClass = str(int(round(img.GMatchVal / roundRange)*roundRange))
        G_Dict[ValClass].append(img.path)
    return G_Dict

def GenerateColorDict(roundRange=200):
    global Images
    C_Dict = {}
    C_Dict['roundrange'] = roundRange
    for r in range(0, 261, roundRange):
        for g in range(0, 261, roundRange):
            for b in range(0, 261, roundRange):
                C_Dict[str(r) + '_' + str(g) + '_' + str(b)] = []
    for img in Images:
        ValClass = str(int(round(img.CMatchVal[0] / roundRange)*roundRange)) + '_' + str(int(round(img.CMatchVal[1] / roundRange)*roundRange)) + '_' + str(int(round(img.CMatchVal[2] / roundRange)*roundRange))
        C_Dict[ValClass].append(img.path)
    return C_Dict

def UpdateJSONFiles(G_Dict, C_Dict, G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json'):
    if G_Dict is not None:
        with open(G_JSON, 'w') as fg:
            json.dump(G_Dict, fg)
    if C_Dict is not None:
        with open(C_JSON, 'w') as fc:
            json.dump(C_Dict, fc)

def AddImagesToDatabase(paths, match_mode='avg', G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json'):
    global Images

    G_Dict = {}
    with open(G_JSON) as fgr:
        G_Dict = json.load(fgr)
    roundRangeG = G_Dict['roundrange']
    C_Dict = {}
    with open(C_JSON) as fcr:
        C_Dict = json.load(fcr)
    roundRangeC = C_Dict['roundrange']
    #progress = 0
    #totfiiles = len(paths)
    print("Adding Images to Database...")
    for path in tqdm(paths):
    # for path in paths:
        if os.path.exists(path):
            img = ImageDetails(path, 0.0, [0.0, 0.0, 0.0])

            if match_mode == 'avg':
                I = cv2.imread(img.path)
                I_g = cv2.imread(img.path, 0)
                img.GMatchVal = np.sum(np.sum(I_g, axis=1), axis=0) / (I_g.shape[0]*I_g.shape[1])
                img.CMatchVal = np.sum(np.sum(I, axis=1), axis=0) / (I.shape[0]*I.shape[1])
            elif match_mode == 'name': # Name is of form Type_SubDirName_000_000_000.png for color
                filename = os.path.splitext(os.path.basename(img.path))[0]
                img.CMatchVal = list(map(int, filename[-11:].split('_'))) 
                img.GMatchVal = int(0.2989 * img.CMatchVal[0] + 0.5870 * img.CMatchVal[1] + 0.1140 * img.CMatchVal[2])
            imgIndex = -1
            for i in range(len(Images)):
                if Images[i].path == img.path:
                    imgIndex = i
                    Images[i].GMatchVal = img.GMatchVal
                    Images[i].CMatchVal = img.CMatchVal
            if imgIndex == -1:
                Images.append(img)
            
            ValClassG = str(int(round(img.GMatchVal / roundRangeG)*roundRangeG))
            G_Dict[ValClassG].append(img.path)

            ValClassC = str(int(round(img.CMatchVal[0] / roundRangeC)*roundRangeC)) + '_' + str(int(round(img.CMatchVal[1] / roundRangeC)*roundRangeC)) + '_' + str(int(round(img.CMatchVal[2] / roundRangeC)*roundRangeC))
            #print(ValClassC, path)
            C_Dict[ValClassC].append(img.path)
            #progress += 1
            #print("Database Added:", progress, "/", totfiiles)

    UpdateJSONFiles(G_Dict, C_Dict, G_JSON, C_JSON)

def AddSolidColorImagesToDatabase(color_step, n_imgs_per_step, Imgsize=(100, 100, 3), match_mode='avg', DatabaseLocation='FillImgs', G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json'):
    paths = []
    print("Creating Solid Color Images...")
    for r in tqdm(range(color_step, 256, color_step)):
        for g in range(color_step, 256, color_step):
            for b in range(color_step, 256, color_step):
                for j in range(n_imgs_per_step):
                    redVal = random.randint(r-color_step, r)
                    greenVal = random.randint(g-color_step, g)
                    blueVal = random.randint(b-color_step, b)
                    img = GenerateSolidColourImage(Imgsize, (redVal, greenVal, blueVal))
                    zeropad = [str('0'*(3 - len(str(redVal)))), str('0'*(3 - len(str(greenVal)))), str('0'*(3 - len(str(blueVal))))]
                    filename = 'SolidColor_' + zeropad[0] + str(redVal) + '_' + zeropad[1] + str(greenVal) + '_' + zeropad[2] + str(blueVal) + '.png'
                    if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                        cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                        paths.append(os.path.join(DatabaseLocation, filename))
                #print("Done Creating:","(" + str(r), ",", str(g) + ",", str(b) + ")")
    AddImagesToDatabase(paths, match_mode, G_JSON=G_JSON, C_JSON=C_JSON)

def AddSolidGreyScaleImagesToDatabase(color_step, n_imgs_per_step, Imgsize=(100, 100), match_mode='avg', DatabaseLocation='FillImgs', G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json'):
    paths = []
    print("Creating GrayScale Images...")
    for g in tqdm(range(color_step, 256, color_step)):
        for j in range(n_imgs_per_step):
            gVal = random.randint(g-color_step, g)
            img = GenerateSolidColourImage(Imgsize, gVal)
            zeropad = str('0'*(3 - len(str(gVal))))
            filename = 'SolidGreyScale_' + zeropad + str(gVal) + '_' + zeropad + str(gVal) + '_' + zeropad + str(gVal) + '.png'
            if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                paths.append(os.path.join(DatabaseLocation, filename))
        #print("Done Creating:", g)
    AddImagesToDatabase(paths, match_mode, G_JSON=G_JSON, C_JSON=C_JSON)

def GenerateSolidColourImage(Imgsize, color):
    return np.ones(Imgsize) * color

def AddColorShiftedImagesToDatabase(refImage, color_step, n_imgs_per_step, refImageName='test', Imgsize=(100, 100, 3), match_mode='name', DatabaseLocation='FillImgs_ColorShift', G_JSON='FillImgs_G_ColorShift.json', C_JSON='FillImgs_C_ColorShift.json'):
    paths = []
    print("Creating Color Shifted Images...")
    for r in tqdm(range(color_step, 256, color_step)):
        for g in range(color_step, 256, color_step):
            for b in range(color_step, 256, color_step):
                for j in range(n_imgs_per_step):
                    AvgColor = [random.randint(r-color_step, r), random.randint(g-color_step, g), random.randint(b-color_step, b)]
                    img = GenerateColorShiftedImage(refImage, AvgColor)
                    zeropad = [str('0'*(3 - len(str(AvgColor[0])))), str('0'*(3 - len(str(AvgColor[1])))), str('0'*(3 - len(str(AvgColor[2]))))]
                    filename = 'ColorShift_' + refImageName + '_' + zeropad[0] + str(AvgColor[0]) + '_' + zeropad[1] + str(AvgColor[1]) + '_' + zeropad[2] + str(AvgColor[2]) + '.png'
                    if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                        cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                        paths.append(os.path.join(DatabaseLocation, filename))
                #print("Done Creating:","(" + str(r), ",", str(g) + ",", str(b) + ")")
    AddImagesToDatabase(paths, match_mode, G_JSON=G_JSON, C_JSON=C_JSON)

def AddGreyScaleShiftedImagesToDatabase(refImage, color_step, n_imgs_per_step, refImageName='test', Imgsize=(100, 100), match_mode='avg', DatabaseLocation='FillImgs_ColorShift', G_JSON='FillImgs_G_GreyScaleShift.json', C_JSON='FillImgs_C_GreyScaleShift.json'):
    paths = []
    print("Creating GrayScale Images...")
    for g in tqdm(range(color_step, 256, color_step)):
        for j in range(n_imgs_per_step):
            AvgScale = random.randint(g-color_step, g)
            img = GenerateColorShiftedImage(refImage, AvgScale)
            zeropad = str('0'*(3 - len(str(AvgScale))))
            filename = 'GreyScaleShift_' + refImageName + '_' + zeropad + str(AvgScale) + '_' + zeropad + str(AvgScale) + '_' + zeropad + str(AvgScale) + '.png'
            if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                paths.append(os.path.join(DatabaseLocation, filename))
        #print("Done Creating:", g)
    AddImagesToDatabase(paths, match_mode, G_JSON=G_JSON, C_JSON=C_JSON)

def GenerateColorShiftedImage(Image, ExpectedAvgColor):
    I = Image.copy().astype(int)
    avgC = np.round(np.sum(np.sum(I, axis=1), axis=0) / (I.shape[0]*I.shape[1])).astype(int)
    AvgDiff = np.clip(ExpectedAvgColor - avgC, 0, 255)
    I = np.clip(np.add(I, AvgDiff), 0, 255)
    return I.astype(np.uint8)

# Driver Code
# DatabaseLocation = 'FillImgs'

# SubDirChoice = '_test'
# JSONSubDir = ''

# DirChoice = '_ColorShift'

# roundRange = 50
# match_mode = 'name'

# RefreshDatabase(DatabaseLocations=[DatabaseLocation + DirChoice + SubDirChoice], G_JSON=DatabaseLocation + '_G' + DirChoice + JSONSubDir + '.json', C_JSON=DatabaseLocation + '_C' + DirChoice + JSONSubDir + '.json', match_mode=match_mode, roundRange=roundRange)

# refImageName = 'test'
# refImageExt = 'jpg'
# color_step = 25
# n_per_step = 2
# refImage = cv2.cvtColor(cv2.imread(refImageName + '.' + refImageExt), cv2.COLOR_BGR2RGB)
# AddColorShiftedImagesToDatabase(refImage, color_step, n_per_step, refImageName=refImageName, Imgsize=(100, 100, 3), match_mode='avg', 
# DatabaseLocation='FillImgs_ColorShift_' + refImageName, 
# G_JSON='FillImgs_G_ColorShift' + JSONSubDir + '.json', C_JSON='FillImgs_C_ColorShift' + JSONSubDir + '.json')

# color_step = 50
# n_per_step = 2
# AddSolidColorImagesToDatabase(color_step, n_per_step, Imgsize=(100, 100, 3), match_mode='avg', 
# DatabaseLocation='FillImgs_SolidColor' + SubDirChoice, 
# G_JSON='FillImgs_G_SolidColor' + JSONSubDir + '.json', C_JSON='FillImgs_C_SolidColor' + JSONSubDir + '.json')

# RefreshDatabase(DatabaseLocations=[DatabaseLocation + DirChoice + SubDirChoice], G_JSON=DatabaseLocation + '_G' + DirChoice + JSONSubDir + '.json', C_JSON=DatabaseLocation + '_C' + DirChoice + JSONSubDir + '.json', match_mode=match_mode, roundRange=roundRange)