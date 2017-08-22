# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client_ui.ui'
#
# Created: Fri Jan 09 13:59:08 2015
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 251)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 210, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        #self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayoutWidget = QtGui.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 30, 361, 161))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.comboBox_serverip = QtGui.QComboBox(self.gridLayoutWidget)
        self.comboBox_serverip.setObjectName(_fromUtf8("comboBox_serverip"))
        
        self.comboBox_serverip.addItems([_fromUtf8("10.37.132.95"), _fromUtf8("10.37.142.99")])
        self.comboBox_serverip.setCurrentIndex(0)
        self.gridLayout.addWidget(self.comboBox_serverip, 0, 1, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_username.setObjectName(_fromUtf8("lineEdit_username"))
        self.gridLayout.addWidget(self.lineEdit_username, 3, 1, 1, 1)
        self.comboBox_duttype = QtGui.QComboBox(self.gridLayoutWidget)
        self.comboBox_duttype.setObjectName(_fromUtf8("comboBox_duttype"))
        self.gridLayout.addWidget(self.comboBox_duttype, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.comboBox_serialport = QtGui.QComboBox(self.gridLayoutWidget)
        self.comboBox_serialport.setObjectName(_fromUtf8("comboBox_serialport"))
        self.gridLayout.addWidget(self.comboBox_serialport, 2, 1, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 0, 2, 1, 1)
        self.label_6 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        self.label_7 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 2, 2, 1, 1)
        self.label_8 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 3, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label_2.setText(_translate("Dialog", "DUT Type", None))
        self.label_3.setText(_translate("Dialog", "Serial Port", None))
        self.label_4.setText(_translate("Dialog", "Owner", None))
        self.label.setText(_translate("Dialog", "Server IP", None))
        self.label_5.setText(_translate("Dialog", "*", None))
        self.label_6.setText(_translate("Dialog", "*", None))
        self.label_7.setText(_translate("Dialog", "*", None))
        self.label_8.setText(_translate("Dialog", "*", None))
        
        
    def setUserName(self, username):
        self.lineEdit_username.insert(_fromUtf8(username))
    def setServerIP(self, serverip):
        if serverip == "10.37.142.99":
            self.comboBox_serverip.setCurrentIndex(1)
            return 
        self.comboBox_serverip.setCurrentIndex(0)
    def setDuttype(self, duttype_list):
        _fromUtf8_duttype_list = []
        for tmp in duttype_list:
            _fromUtf8_duttype_list.append(_fromUtf8(tmp))
        self.comboBox_duttype.addItems(_fromUtf8_duttype_list)
        self.comboBox_duttype.setCurrentIndex(0)
    def setSerialPort(self, serialport_list):
        _fromUtf8_serialport_list = []
        for tmp in serialport_list:
            _fromUtf8_serialport_list.append(_fromUtf8(str(tmp)))
        self.comboBox_serialport.addItems(_fromUtf8_serialport_list)
        self.comboBox_serialport.setCurrentIndex(0)



#继承的类要和生成的ui对相
class Client_Ui(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Client_Ui, self).__init__(parent)    
        self.ui = Ui_Dialog()        
        self.ui.setupUi(self)

def getServerIP():
    return "10.37.142.99"
def getSerialPort():
    return [1, 3, 5, 8]
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    window = Client_Ui()
    window.show()
    window.ui.setServerIP(getServerIP())
    window.ui.setDuttype(getDUTType())
    window.ui.setSerialPort(getSerialPort())
    window.ui.setUserName(getUserName())
    sys.exit(app.exec_())
