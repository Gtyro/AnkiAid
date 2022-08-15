from os import remove
from os.path import isfile
import re
import sys

from bs4 import BeautifulSoup
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QApplication, QWidget, QPlainTextEdit, QMainWindow, QMessageBox
import requests
import win32clipboard as w

from clipboard import getclipboard, setclipboard
from Ui_ankiaid import *


mapL = {"v.":"pos_v",
        "vi.":"pos_v",
        "vt.":"pos_v",
        "n.":"pos_n",
        "prep.":"pos_p",
        "conj.":"pos_c",
        "adv.":"pos_r",
        "adj.":"pos_a"}

cardtxtname = "tmp.txt"
ankipath = "D:\Program Files\Anki\Anki"

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.word = ''
        self.card = None
        self.inputLine.setAttribute(QtCore.Qt.WidgetAttribute.WA_InputMethodEnabled, False) # 禁用输入法
        actHelp = QAction("Help", self)
        actHelp.triggered.connect(self.help)
        self.menubar.addAction(actHelp)
    
    def help(self):
        """display the help information"""
        QMessageBox.information(self, "帮助", "enter a word and press enter key")

    def keyPressEvent(self, event):
        """respond to key-down events"""
        key = event.key()
        modifier = QApplication.keyboardModifiers()
        if (key == Qt.Key_V) and modifier == Qt.ControlModifier:
            print("paste word")
            self.inputLine.setText(getclipboard())
            return
        if (key == Qt.Key_Return): # enter corresponds to Key_Return?
            print("make & import")
            self.mkcard()
            self.impCard()
            return
        if (key == Qt.Key_I) and modifier == Qt.ControlModifier|Qt.ShiftModifier:
            print("simply import")
            self.impCard()
            return
        if (key == Qt.Key_X) and modifier == Qt.ControlModifier|Qt.ShiftModifier:
            print("switch mode")
            self.switchMode()
            return

    def switchMode(self):
        """switch mode between html and plain text"""
        text = self.dispArea.toPlainText()

        for key in mapL.keys():
            text = text.replace(key, "<a class=\"{}\">{}</a>".format(mapL[key], key))
        
        if self.dispArea.styleSheet():
            self.dispArea.setStyleSheet("")
            text = text.replace("\n", "<br>")
            self.dispArea.setText(text)
        else:
            self.dispArea.setStyleSheet("color: white;background-color: black")
            self.dispArea.setPlainText(text)
        setclipboard(text)

    def impCard(self):
        """import card into Anki"""
        with open(cardtxtname, "w", encoding="utf-8") as f:
            f.write("\t".join([word for word in self.card])) # .replace("\n", "&nbsp;")
        from os import system as osys, popen
        # osys(f'start "{ankipath}" {cardtxtname}')
        popen(f'"{ankipath}" {cardtxtname}')

    def genHref(self):
        """generate a href link"""
        self.word = self.inputLine.text()
        #
        '''
        https://www.youdao.com/result?word=%s&lang=en
        '''
        text = '<a href="https://www.youdao.com/result?word={0}&lang=en">{0}</a>'.format(self.word)
        self.dispArea.setPlainText(text)
        setclipboard(text)
        #
        pass

    def mkcard(self):
        """make the card"""
        # print("mkcard")
        if self.word == self.inputLine.text():
            self.impCard()
            return
        self.word = self.inputLine.text()

        ## 判断输入正确性
        # 本地判断
        if self.word == "":
            # print("no input")
            QMessageBox.warning(self, str(self.inputLine.__class__), "No input")
            return
        if not re.match("[a-z-]+", self.word):
            # print("unrecognized characters")
            QMessageBox.information(self, str(self.inputLine.__class__), "unrecognized characters")
            return
        '''
        from enchant import Dict
        d = Dict("en_US")
        if not d.check(self.word):
            QMessageBox.warning(self, str(self.inputLine.__class__), "我们不认你这个词")
            return
        '''
        
        url = "https://www.youdao.com/result?word=%s&lang=en"%self.word
        r = requests.get(url,timeout=0.3)
        soup = BeautifulSoup(r.text,features="lxml")

        # 联网判断
        title = soup.find(class_ = "title")
        if not title and not title.find(class_ = "word-operate add"):
            QMessageBox.warning(self, str(self.inputLine.__class__), "Not found in Youdao.com")
            return

        # 刷新
        self.dispArea.setStyleSheet("")

        # 获取音标
        phonetic = ' '.join([i.text for i in soup.find_all(class_ = "per-phone")])
        # 中文释义
        ## 在此处预防可能出现的字符串误匹配问题
        wordexp = "<br>".join([re.compile("([a-z]+\.)").sub(lambda m:f"<a class='{mapL[m.group(0)]}'>{m.group(0)}</a>",string=i.text) for i in soup.find_all("li", class_ = "word-exp")])
        # 英语例句
        _ = [sen.text for sen in soup.find_all(class_ = "sen-eng")]
        sen_eng = "<br>".join([f"({i+1}) "+_[i] for i in range(len(_))])

        # 中文例句
        _ = [sen.text for sen in soup.find_all(class_ = "sen-ch")]
        sen_ch = "<br>".join([f"({i+1}) "+_[i] for i in range(len(_))])
        
        # vocabulary简明
        # vocabulary扩展
        # 柯林斯星级
        # 柯林斯解释

        # 英语发音
        pronunciation = "[sound:http://dict.youdao.com/dictvoice?type=0&audio={{%s}}]"%self.word
        
        text = "<br>".join([self.word, phonetic, wordexp, sen_eng, sen_ch, pronunciation])
        self.dispArea.setHtml(text)
        def genCard():
            card = [
                self.word,
                # f'"{phonetic}"',
                phonetic,
                "\"{}\"".format(wordexp.replace('\"', '\"\"')),
                "",
                sen_eng,
                sen_ch,
                "",
                "",
                "",
                "",
                pronunciation,
                "大学六级英语单词"
            ]
            return card
        self.card = genCard()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    exit_code = app.exec_()

    if isfile(cardtxtname):
        # 异常处理
        remove(cardtxtname)
        
    sys.exit(exit_code)