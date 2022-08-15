"""
剪切板操作
last edited: 2022-08-13
"""

import win32clipboard as w

def getclipboard()->str:
    if not w.IsClipboardFormatAvailable(w.CF_UNICODETEXT):
        print("NOT CF_UNICODETEXT FORMAT")
        return ""
    if w.OpenClipboard():
        print("OpenClipboard failure")
        return ""
    data = w.GetClipboardData()
    w.CloseClipboard()
    return data

def setclipboard(string):
    if not isinstance(string, str):
        print("not string")
        return False
    if w.OpenClipboard():
        print("OpenClipboard failure")
        return
    w.EmptyClipboard()
    w.SetClipboardData(w.CF_UNICODETEXT, string)
    w.CloseClipboard()