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
        for dirpath, dirnames, filenames in tqdm(os.walk(DatabaseLocation)):
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
            Images[i].CMatchVal = np.sum(np.sum(I, axis=1), axis=0) / (I.shape[0]*I.shape[1])
            Images[i].GMatchVal = int(np.mean(Images[i].CMatchVal))
        elif match_mode == 'name': # Name is of form Type_SubDirName_000_000_000.png for color
            filename = os.path.splitext(os.path.basename(Images[i].path))[0]
            Images[i].CMatchVal = np.array(map(int, filename.split('_')[-3:])) 
            # Images[i].GMatchVal = int(0.2989 * Images[i].CMatchVal[0] + 0.5870 * Images[i].CMatchVal[1] + 0.1140 * Images[i].CMatchVal[2])
            Images[i].GMatchVal = int(np.mean(Images[i].CMatchVal))
    
def GenerateGreyScaleDict(roundRange=100):
    global Images
    G_Dict = {}
    G_Dict['roundRange'] = roundRange
    print("Generating GrayScale JSON Dictionary...")
    for i in range(0, 256, roundRange):
        G_Dict[str(i)] = []
    for img in tqdm(Images):
        ValClass = str(int(img.GMatchVal - (img.GMatchVal % roundRange)))
        G_Dict[ValClass].append(img.path)
    return G_Dict

def GenerateColorDict(roundRange=200):
    global Images
    C_Dict = {}
    C_Dict['roundRange'] = roundRange
    print("Generating Color JSON Dictionary...")
    for r, g, b in range(0, 256, roundRange), range(0, 256, roundRange), range(0, 256, roundRange):
        C_Dict['_'.join(map(str, [r, g, b]))] = []
    for img in tqdm(Images):
        ValClass = '_'.join(map(str, list(img.CMatchVal - (img.CMatchVal % roundRange))))
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
    roundRangeG = G_Dict['roundRange']
    C_Dict = {}
    with open(C_JSON) as fcr:
        C_Dict = json.load(fcr)
    roundRangeC = C_Dict['roundRange']
    #progress = 0
    #totfiiles = len(paths)
    print("Adding Images to Database...")
    for path in tqdm(paths):
        if os.path.exists(path):
            img = ImageDetails(path, 0.0, [0.0, 0.0, 0.0])

            if match_mode == 'avg':
                I = cv2.imread(img.path)
                img.CMatchVal = np.sum(np.sum(I, axis=1), axis=0) / (I.shape[0]*I.shape[1])
                img.GMatchVal = int(np.mean(img.CMatchVal))
            elif match_mode == 'name': # Name is of form Type_SubDirName_000_000_000.png for color
                filename = os.path.splitext(os.path.basename(img.path))[0]
                img.CMatchVal = np.array(map(int, filename.split('_')[-3:]))
                # img.GMatchVal = int(0.2989 * img.CMatchVal[0] + 0.5870 * img.CMatchVal[1] + 0.1140 * img.CMatchVal[2])
                img.GMatchVal = int(np.mean(img.CMatchVal))

            # Check if path already exists in database - Update values or add image
            imgFound = False
            for i in range(len(Images)):
                if Images[i].path == img.path:
                    imgFound = True
                    Images[i].GMatchVal = img.GMatchVal
                    Images[i].CMatchVal = img.CMatchVal
            if imgFound == False:
                Images.append(img)
            
            ValClassG = str(int(img.GMatchVal - (img.GMatchVal % roundRangeG)))
            G_Dict[ValClassG].append(img.path)

            ValClassC = '_'.join(map(str, list(img.CMatchVal - (img.CMatchVal % roundRangeC))))
            C_Dict[ValClassC].append(img.path)
            #progress += 1
            #print("Database Added:", progress, "/", totfiiles)

    UpdateJSONFiles(G_Dict, C_Dict, G_JSON, C_JSON)

def AddSolidColorImagesToDatabase(color_step, n_imgs_per_step, Imgsize=(100, 100, 3), match_mode='avg', DatabaseLocation='FillImgs', G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json'):
    paths = []
    if n_imgs_per_step > color_step:
        n_imgs_per_step = color_step

    print("Creating Solid Color Images...")
    for r, g, b in tqdm(range(color_step, 256, color_step), range(color_step, 256, color_step), range(color_step, 256, color_step)):
        redVal = np.random.randint(r-color_step, r, n_imgs_per_step)
        greenVal = np.random.randint(g-color_step, g, n_imgs_per_step)
        blueVal = np.random.randint(b-color_step, b, n_imgs_per_step)
        for i in range(n_imgs_per_step):
            img = GenerateSolidColourImage(Imgsize, (redVal, greenVal, blueVal))
            filename = 'SolidColor_' + '_'.join(map(str, [redVal[i], greenVal[i], blueVal[i]])) + '.png'
            if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                paths.append(os.path.join(DatabaseLocation, filename))

    AddImagesToDatabase(paths, match_mode, G_JSON=G_JSON, C_JSON=C_JSON)

def AddSolidGreyScaleImagesToDatabase(color_step, n_imgs_per_step, Imgsize=(100, 100), match_mode='avg', DatabaseLocation='FillImgs', G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json'):
    paths = []
    if n_imgs_per_step > color_step:
        n_imgs_per_step = color_step

    print("Creating GrayScale Images...")
    for g in tqdm(range(color_step, 256, color_step)):
        gVal = np.random.randint(g-color_step, g, n_imgs_per_step)
        for j in range(n_imgs_per_step):
            img = GenerateSolidColourImage(Imgsize, gVal[i])
            filename = 'SolidGreyScale_' + '_'.join(map(str, [gVal[i], gVal[i], gVal[i]])) + '.png'
            if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                paths.append(os.path.join(DatabaseLocation, filename))

    AddImagesToDatabase(paths, match_mode, G_JSON=G_JSON, C_JSON=C_JSON)

def GenerateSolidColourImage(Imgsize, color):
    return np.ones(Imgsize) * color

def AddColorShiftedImagesToDatabase(refImage, color_step, n_imgs_per_step, refImageName='test', Imgsize=(100, 100, 3), match_mode='name', DatabaseLocation='FillImgs_ColorShift', G_JSON='FillImgs_G_ColorShift.json', C_JSON='FillImgs_C_ColorShift.json'):
    paths = []
    print("Creating Color Shifted Images...")
    for r, g, b in tqdm(range(color_step, 256, color_step), range(color_step, 256, color_step), range(color_step, 256, color_step)):
        redVal = np.random.randint(r-color_step, r, n_imgs_per_step)
        greenVal = np.random.randint(g-color_step, g, n_imgs_per_step)
        blueVal = np.random.randint(b-color_step, b, n_imgs_per_step)
        for i in range(n_imgs_per_step):
            AvgColor = [redVal[i], greenVal[i], blueVal[i]]
            img = GenerateColorShiftedImage(refImage, AvgColor)
            filename = 'ColorShift_' + refImageName + '_' + '_'.join(map(str, AvgColor)) + '.png'
            if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                paths.append(os.path.join(DatabaseLocation, filename))

    AddImagesToDatabase(paths, match_mode, G_JSON=G_JSON, C_JSON=C_JSON)

def AddGreyScaleShiftedImagesToDatabase(refImage, color_step, n_imgs_per_step, refImageName='test', Imgsize=(100, 100), match_mode='avg', DatabaseLocation='FillImgs_ColorShift', G_JSON='FillImgs_G_GreyScaleShift.json', C_JSON='FillImgs_C_GreyScaleShift.json'):
    paths = []
    print("Creating GrayScale Images...")
    for g in tqdm(range(color_step, 256, color_step)):
        gVal = np.random.randint(g-color_step, g, n_imgs_per_step)
        for i in range(n_imgs_per_step):
            AvgScale = gVal[i]
            img = GenerateColorShiftedImage(refImage, AvgScale)
            filename = 'GreyScaleShift_' + refImageName + '_' + '_'.join(map(str, AvgScale)) + '.png'
            if not os.path.exists(os.path.join(DatabaseLocation, filename)):
                cv2.imwrite(os.path.join(DatabaseLocation, filename), img)
                paths.append(os.path.join(DatabaseLocation, filename))
    
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