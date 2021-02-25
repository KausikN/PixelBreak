'''
UI script for ImageDatabase
'''

# Imports
from UIUtils import Py2UI

# Main Functions
def UITextSelectParser(text):
    text = "'" + text + "'"
    return text

# Driver Code
# Params
jsonPath = 'UIUtils/ImageDatabaseUI.json'

specialCodeProcessing = {"MainFunctions": UITextSelectParser, "AdditionalFunctions": UITextSelectParser}
# Params

# RunCode
Py2UI.JSON2UI(jsonPath, specialCodeProcessing)