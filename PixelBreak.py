'''
Summary
This is a script to break down an image into set of images which when placed together and viewed roughly reconstructs the original image
'''
import cv2
import numpy as np
import json
import random
import matplotlib.pyplot as plt
from tqdm import tqdm

fillImg_G_dict = {}
fillImgIndex_G_dict = {}
fillImg_C_dict = {}
fillImgIndex_C_dict = {}
BoundingBoxRadius = 3

def ImageBreak(originalImage, window_size, match_mode, fillImageSize=(100, 100), nextImageMode='increment', DisplayIntermiateSteps=True):
    global BoundingBoxRadius
    newImage = None
    colorImg = (originalImage.ndim == 3)
    if not colorImg:
        newImageSize = (fillImageSize[0]*(int(round(originalImage.shape[0] / window_size[0])) + 1),
                        fillImageSize[1]*(int(round(originalImage.shape[1] / window_size[1])) + 1))
    else:
        newImageSize = (fillImageSize[0]*(int(round(originalImage.shape[0] / window_size[0])) + 1),
                        fillImageSize[1]*(int(round(originalImage.shape[1] / window_size[1])) + 1),
                        originalImage.shape[2])
    newImage = np.zeros(newImageSize, dtype=np.uint8)

    ni = 0
    nj = 0

    for i in tqdm(range(0, originalImage.shape[0], window_size[0])):
        nj = 0
        for j in range(0, originalImage.shape[1], window_size[1]):
            if match_mode == 'avg':
                ImageWindowPortion = None
                if (i+window_size[0] < originalImage.shape[0] and j+window_size[1] < originalImage.shape[1]):
                    ImageWindowPortion = originalImage[i:i+window_size[0], j:j+window_size[1]]
                else:
                    ImageWindowPortion = originalImage[i:, j:]
                AvgPixVal = AveragePixelValue(ImageWindowPortion)
                #print("Matching: ", ni*fillImageSize[0], (ni+1)*fillImageSize[0], nj*fillImageSize[1], (nj+1)*fillImageSize[1])
                newImage[ni*fillImageSize[0]:(ni+1)*fillImageSize[0], nj*fillImageSize[1]:(nj+1)*fillImageSize[1]] = ResizeImage(GetMatchingImage(AvgPixVal, match_mode, colorImg, nextImageMode=nextImageMode), fillImageSize)
                zerocheck = np.sum(np.sum(newImage[ni*fillImageSize[0]:(ni+1)*fillImageSize[0], nj*fillImageSize[1]:(nj+1)*fillImageSize[1]], axis=1), axis=0)
                if DisplayIntermiateSteps and not zerocheck == 0.0:
                    originalImage_WindowHighlighted = BoundingBox(originalImage, [i, j], window_size, radius=BoundingBoxRadius, color=[50, 50, 50])
                    axw = plt.subplot(2, 2, 1)
                    plt.imshow(originalImage_WindowHighlighted, 'gray')
                    axw.title.set_text('OriginalImg')
                    axw = plt.subplot(2, 2, 2)
                    plt.imshow(ImageWindowPortion, 'gray')
                    axw.title.set_text('WindowPortion')
                    axp = plt.subplot(2, 2, 3)
                    plt.imshow(newImage[ni*fillImageSize[0]:(ni+1)*fillImageSize[0], nj*fillImageSize[1]:(nj+1)*fillImageSize[1]], 'gray')
                    axp.title.set_text('DBImgPortion')
                    ax = plt.subplot(2, 2, 4)
                    plt.imshow(newImage, 'gray')
                    ax.title.set_text('FullSplitImg')
                    plt.show()
                    #DisplayIntermiateSteps = (input("Disp: ") == '')
            nj += 1
        ni += 1
        
    return newImage


def LoadFillImagesData(G_JSON='FillImgs_G.json', C_JSON='FillImgs_C.json'):
    global fillImg_G_dict
    global fillImgIndex_G_dict
    global fillImg_C_dict
    global fillImgIndex_C_dict
    with open(G_JSON) as f:
        fillImg_G_dict = json.load(f)
    for key in fillImg_G_dict.keys():
        fillImgIndex_G_dict[key] = 0
    with open(C_JSON) as f:
        fillImg_C_dict = json.load(f)
    for key in fillImg_C_dict.keys():
        fillImgIndex_C_dict[key] = 0

                    
                    
def GetMatchingImage(MatchVal, match_mode, colorImg, nextImageMode='increment'):
    global fillImg_G_dict
    global fillImgIndex_G_dict
    global fillImg_C_dict
    global fillImgIndex_C_dict

    if not colorImg:
        if match_mode in ['avg', 'min', 'max', 'median', 'mode']:
            ValClass = str(int(MatchVal - (MatchVal % fillImg_C_dict['roundRange'])))
            #print("MatchClass:", ValClass, " - Found DBImgs:", len(fillImg_G_dict[ValClass]))
            if len(fillImg_G_dict[ValClass]) > 0:
                #print("Using ImgIndex:", fillImgIndex_G_dict[ValClass])
                fillImgPath = fillImg_G_dict[ValClass][fillImgIndex_G_dict[ValClass]]
                if nextImageMode == 'increment':
                    fillImgIndex_G_dict[ValClass] = int((fillImgIndex_G_dict[ValClass] + 1) % len(fillImg_G_dict[ValClass]))
                elif nextImageMode == 'random':
                    fillImgIndex_G_dict[ValClass] = random.randint(0, len(fillImg_G_dict[ValClass])-1)
                return cv2.imread(fillImgPath, 0)
            else:
                return np.zeros((1, 1))
    else:
        if match_mode in ['avg', 'min', 'max', 'median', 'mode']:
            MatchVal = np.array(MatchVal)
            ValClass = '_'.join(map(str, list(MatchVal - (MatchVal % fillImg_G_dict['roundRange']))))
            #print("MatchClass:", ValClass, " - Found DBImgs:", len(fillImg_C_dict[ValClass]))
            if len(fillImg_C_dict[ValClass]) > 0:
                #print("Using ImgIndex:", fillImgIndex_C_dict[ValClass])
                fillImgPath = fillImg_C_dict[ValClass][fillImgIndex_C_dict[ValClass]]
                if nextImageMode == 'increment':
                    fillImgIndex_C_dict[ValClass] = int((fillImgIndex_C_dict[ValClass] + 1) % len(fillImg_C_dict[ValClass]))
                elif nextImageMode == 'random':
                    fillImgIndex_C_dict[ValClass] = random.randint(0, len(fillImg_C_dict[ValClass])-1)
                return cv2.imread(fillImgPath)
            else:
                return np.zeros((1, 1, len(list(MatchVal))))

def ResizeImage(Image, fillImgSize):
    fillImgSize = tuple(fillImgSize)
    return cv2.resize(Image, fillImgSize)


def AveragePixelValue(Image):
    return (np.sum(np.sum(Image, axis=1), axis=0) / (Image.shape[0]*Image.shape[1])).astype(int)

def BoundingBox(Image, pos, window_size, radius=1, color=[0, 0, 0]):
    I = Image.copy()
    window_size = [window_size[0], window_size[1]]
    for wi in range(len(window_size)):
        if pos[wi] + window_size[wi] > Image.shape[wi]:
            window_size[wi] = Image.shape[wi] - pos[wi]
    
    if I.ndim == 2:
        for i in [pos[0], pos[0] + window_size[0]]:
            for p in range(pos[1], pos[1] + window_size[1]):
                I[i, p] = color[0]
                #print("Markx:", i, p, color[0])
        for j in [pos[1], pos[1] + window_size[1]]:
            for p in range(pos[0], pos[0] + window_size[0]):
                I[p, j] = color[0]
                #print("Marky:", p, j, color[0])
    elif I.ndim == 3:
        for i in [pos[0], pos[0] + window_size[0]]:
            for p in range(pos[1], pos[1] + window_size[1]):
                I[i, p, :] = color
        for j in [pos[1], pos[1] + window_size[1]]:
            for p in range(pos[0], pos[0] + window_size[0]):
                I[p, j, :] = color

    for ri in range(1, radius+1):
        I = BoundingBox(I, [pos[0]+ri, pos[1]+ri], [window_size[0]-(2*ri), window_size[1]-(2*ri)], radius=0, color=color)
    return I

# Driver Code

SubDirName = '_ColorShift'
G_JSON = 'FillImgs_G' + SubDirName + '.json'
C_JSON = 'FillImgs_C' + SubDirName + '.json'
LoadFillImagesData(G_JSON=G_JSON, C_JSON=C_JSON)

# # Params
# ImagePath = 'TestImgs/FunctionStandardFormat_1.png'
# GrayScaleInput = False

# splitImgSavePath = 'GeneratedImgs/SplitImage3.png'

# window_size = (50, 50)
# match_mode = 'avg'
# fillImageSize=(50, 50)
# nextImageMode = 'random'

# DisplayIntermiateSteps = False
# # Params

# I = None
# if GrayScaleInput:
#     I = cv2.imread(ImagePath, 0)
#     plt.imshow(I, 'gray')
# else:
#     I = cv2.imread(ImagePath)
#     plt.imshow(cv2.cvtColor(I, cv2.COLOR_BGR2RGB))
# plt.show()
# print("Input Image Shape:", I.shape)

# splitImage = ImageBreak(I, window_size, match_mode, fillImageSize, nextImageMode=nextImageMode, DisplayIntermiateSteps=DisplayIntermiateSteps)
# cv2.imwrite(splitImgSavePath, splitImage)
# plt.figure()
# plt.title('Final Split Image')

# if GrayScaleInput:
#     plt.imshow(splitImage.astype(np.uint8), 'gray')
# else:
#     plt.imshow(cv2.cvtColor(splitImage.astype(np.uint8), cv2.COLOR_BGR2RGB))
# plt.show()

# # III = BoundingBox(I, [100, 0], [100, 100], radius=3, color=[0, 0, 0])
# # plt.imshow(III, 'gray')
# # plt.show()
