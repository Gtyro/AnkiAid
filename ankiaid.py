import sys,re
from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit
from Ui_ankiaid import *
import win32clipboard as w
import requests
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup
sys.path.insert(0,r"D:\Users\10941\source\repos\Python")
from tools.timer计时 import mark,printTfLT

style = """
    <a style = 
    'text-decoration: none;
    padding: 1px 6px 2px 5px;
	margin: 0 5px 0 0;
	font-size: 12px;
	color: white;
	font-weight: normal;
	border-radius: 4px'>style</a>
    """.replace('\n','')

mapL = {"v.":"pos_v",
        "vi.":"pos_v",
        "vt.":"pos_v",
        "n.":"pos_n",
        "prep.":"pos_r",
        "conj.":"pos_r",
        "adv.":"pos_r",
        "adj.":"pos_a"}

def getStag(pos:str):
    return f"<a class='{mapL[pos]}'>{pos}</a>"
    pass

def getclipboard():
    w.OpenClipboard()
    data = w.GetClipboardData()
    w.CloseClipboard()
    return data

def setclipboard(string):
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(w.CF_UNICODETEXT, string)
    w.CloseClipboard()

class MyWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.word = str()
        self.lineEdit.setAttribute(QtCore.Qt.WidgetAttribute.WA_InputMethodEnabled, False) #禁用输入法
        self.pushButton.clicked.connect(self.onInputChanged)
        self.pushButton_2.clicked.connect(self.onInputChanged2)
        self.pushButton_3.clicked.connect(self.onInputChanged3)
        self.pushButton_4.clicked.connect(self.onInputChanged4)
        self.pushButton_5.clicked.connect(self.init)
        self.pushButton_link.clicked.connect(self.genHref)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_V) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.lineEdit.setText(getclipboard())
            return
        if (event.key() == Qt.Key_Z) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.lineEdit.setText("")
            return

    def getW(self):
        word = self.lineEdit.text()
        return word

    def freshW(self):
        """self.word = self.lineEdit.text()"""
        # if self.word == '': # 刚开始，没有词
        #     self.word = self.lineEdit.text()
        if self.word != self.lineEdit.text(): # 重新写了词
            self.word = self.lineEdit.text()

    def onInputChanged(self,text):
        """词性高亮"""
        if text == "":
            text = self.plainTextEdit.toPlainText()
        self.plainTextEdit.setPlainText(text)
        textlines = text.split()
        for line in textlines:
            pass
        text = text.replace("n.", "<a class='pos_n'>n.</a>")
        text = text.replace("adj.", "<a class='pos_a'>adj.</a>")
        text = text.replace("adv.", "<a class='pos_r'>adv.</a>")
        text = text.replace("v.", "<a class='pos_v'>v.</a>")
        text = text.replace("vi.", "<a class='pos_v'>vi.</a>")
        text = text.replace("vt.", "<a class='pos_v'>vt.</a>")
        text = text.replace("prep.", "<a class='pos_n'>prep.</a>")
        text = text.replace("conj.", "<a class='pos_r'>conj.</a>")
        text = text.replace('\n',"<br>")
        setclipboard(text)

    def onInputChanged2(self):
        """获取音标"""
        mark()
        self.freshW()
        #
        url = "https://www.youdao.com/result?word=%s&lang=en"%self.word
        html = requests.get(url,timeout=0.3)
        # print(html.text)
        soup = BeautifulSoup(html.text,features="lxml")
        text = ' '.join([i.text for i in soup.find_all(class_ = "per-phone")])
        # self.onInputChanged(text)
        self.plainTextEdit.setPlainText(text)
        setclipboard(text)
        #
        printTfLT("用时")
        # self.plainTextEdit.setPlainText(soup.)

    def onInputChanged3(self):
        """获取释义 + 词性高亮"""
        mark()
        self.freshW()
        #
        url = "https://www.youdao.com/result?word=%s&lang=en"%self.word

        # html一般无换行符\n
        '''
        soup.find_all("li", class_ = "word-exp")    <class 'bs4.element.ResultSet'>     list
        '''
        text = requests.get(url, timeout=0.4).text
        text = "<br>".join([re.compile("([a-z]+\.)").sub(lambda m:f"<a class='{mapL[m.group(0)]}'>{m.group(0)}</a>",string=i.text) for i in BeautifulSoup(text, "lxml").find_all("li", class_ = "word-exp")])
        # self.onInputChanged(text)
        self.plainTextEdit.setPlainText(text)
        setclipboard(text)
        #
        printTfLT("用时")
        pass
        
    def onInputChanged4(self):
        """生成发音"""
        # if self.word == '':
        self.word = self.lineEdit.text()
        #
        '''
        [sound:http://dict.youdao.com/dictvoice?type=0&audio={{}}]
        '''
        text = "[sound:http://dict.youdao.com/dictvoice?type=0&audio={{%s}}]"%self.word
        self.plainTextEdit.setPlainText(text)
        setclipboard(text)
        #
        pass

    def genHref(self):
        """生成链接"""
        self.freshW()
        #
        '''
        https://www.youdao.com/result?word=%s&lang=en
        '''
        text = '<a href="https://www.youdao.com/result?word={0}&lang=en">{0}</a>'.format(self.word)
        self.plainTextEdit.setPlainText(text)
        setclipboard(text)
        #
        pass

    def init(self):
        """豪华套餐"""
        self.freshW()
        if self.word == "":
            """没词"""
            print("没词")
            return
        url = "https://www.youdao.com/result?word=%s&lang=en"%self.word
        r = requests.get(url,timeout=0.3)
        soup = BeautifulSoup(r.text,features="lxml")
        # 获取音标
        phonetic = ' '.join([i.text for i in soup.find_all(class_ = "per-phone")])
        # 中文释义
        wordexp = "<br>".join([re.compile("([a-z]+\.)").sub(lambda m:f"<a class='{mapL[m.group(0)]}'>{m.group(0)}</a>",string=i.text) for i in soup.find_all("li", class_ = "word-exp")])
        # 英语例句
        _ = [sen.text for sen in soup.find_all(class_ = "sen-eng")]
        sen_eng = "<br>".join([f"({i+1}) "+_[i] for i in range(len(_))])
        # print(sen_eng)

        # 中文例句
        _ = [sen.text for sen in soup.find_all(class_ = "sen-ch")]
        sen_ch = "<br>".join([f"({i+1}) "+_[i] for i in range(len(_))])

        # 英语发音
        pronunciation = "[sound:http://dict.youdao.com/dictvoice?type=0&audio={{%s}}]"%self.word
        text = "\n".join([self.word, phonetic, wordexp, sen_eng, sen_ch, pronunciation])
        self.plainTextEdit.setPlainText(text)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())