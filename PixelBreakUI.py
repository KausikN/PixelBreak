'''
UI script for PixelBreak
'''

# Imports
from UIUtils import Py2UI

# Main Functions
def UITextSelectParser(text):
    text = "'" + text + "'"
    return text

# Driver Code
# Params
jsonPath = 'UIUtils/PixelBreakUI.json'

specialCodeProcessing = {"match_mode": UITextSelectParser, "nextImageMode": UITextSelectParser}
# Params

# RunCode
Py2UI.JSON2UI(jsonPath, specialCodeProcessing)