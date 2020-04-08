from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
import json

class Ui_MainWindow(object):
    def __init__(self):
        #Parameters
        self.N = 2096
        self.nt = 4.0 #Periods to plot
        self.dt = 0.01 #Seconds

        self.rate = 15.0/60 #Breaths per minute default value
        self.defaultRate = 15
        self.T = 1/self.rate
        self.dt = self.nt * self.T / self.N
        self.maxRate = 30
        self.minRate = 5

        self.tidalVolume = 500
        self.defaultTidalVolume = 500
        self.maxTidalVolume = 1500
        self.minTidalVolume = 100

        self.baseVolume = 1700
        self.defaultBaseVolume = 1700
        self.maxBaseVolume = 2500
        self.minBaseVolume = 1000

        self.maxPos = 89 #mm
        self.maxVel = 200 #mm/s
        self.maxAccel = 254 #mm/s^2

        self.defaultHomePos = 80 #mm
        self.minHomePos = 40 #mm
        self.maxHomePos = 80 #mm
        self.homePos = self.defaultHomePos
        self.homeVol = 1700 #ml

        self.maxVals = [self.maxPos, self.maxVel, self.maxAccel, self.maxAccel]
        self.vals = [[self.homePos,30,254,254] for i in range(4)]
        self.runPattern = [[self.homePos,30,254,254] for i in range(16)]

        self.diam = 14 #cm
        self.pistonArea = (np.pi/4) * self.diam**2

        self.tAct = np.linspace(0,self.T*self.nt,self.N)
        self.vAct = np.ones(self.N)*self.baseVolume

        self.dontUpdateTable = False

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1506, 800)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.rateInput = QtWidgets.QLineEdit(self.centralwidget)
        self.rateInput.setGeometry(QtCore.QRect(10, 80, 191, 21))
        self.rateInput.setText("")
        self.rateInput.setObjectName("rateInput")
        self.rateInput.setPlaceholderText(str(self.rate*60))

        self.tidalVolumeInput = QtWidgets.QLineEdit(self.centralwidget)
        self.tidalVolumeInput.setGeometry(QtCore.QRect(10, 140, 191, 21))
        self.tidalVolumeInput.setText("")
        self.tidalVolumeInput.setObjectName("tidalVolumeInput")
        self.tidalVolumeInput.setPlaceholderText(str(self.tidalVolume))

        self.rateLabel = QtWidgets.QLabel(self.centralwidget)
        self.rateLabel.setGeometry(QtCore.QRect(10, 50, 321, 21))
        self.rateLabel.setObjectName("rateLabel")

        self.tidalVolumeLabel = QtWidgets.QLabel(self.centralwidget)
        self.tidalVolumeLabel.setGeometry(QtCore.QRect(10, 110, 261, 21))
        self.tidalVolumeLabel.setObjectName("tidalVolumeLabel")

        self.baseVolumeLabel = QtWidgets.QLabel(self.centralwidget)
        self.baseVolumeLabel.setGeometry(QtCore.QRect(10, 170, 291, 31))
        self.baseVolumeLabel.setObjectName("baseVolumeLabel")

        self.baseVolumeInput = QtWidgets.QLineEdit(self.centralwidget)
        self.baseVolumeInput.setGeometry(QtCore.QRect(10, 200, 191, 21))
        self.baseVolumeInput.setText("")
        self.baseVolumeInput.setObjectName("baseVolumeInput")
        self.baseVolumeInput.setPlaceholderText(str(self.baseVolume))

        self.graphicsView = pg.GraphicsLayoutWidget(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(10, 290, 1051, 471))
        self.graphicsView.setObjectName("graphicsView")
        self.plt = self.graphicsView.addPlot(labels={'left':'Lung Volume (mL)', 'bottom':'Time (sec)'})
        self.updatePlot()

        self.sliders = [[],[],[],[]]
        pvad = 'pvad'
        for i in range(4): #p,v,a,d
            x = 1140 if i == 0 or i == 2 else 1330
            y = 80 if i == 0 or i == 1 else 340
            default = self.homePos if i == 0 else 30 if i == 1 else 254

            for j in range(4): #move 1,2,3,4
                self.sliders[i].append(QtWidgets.QSlider(self.centralwidget))
                self.sliders[i][j].setGeometry(QtCore.QRect(x + j*40, y, 20, 161))
                self.sliders[i][j].setOrientation(QtCore.Qt.Vertical)
                self.sliders[i][j].setObjectName(pvad[i] + str(j+1) + 'Slider')
                self.sliders[i][j].setMaximum(500)
                self.sliders[i][j].setValue(int(default * 500/self.maxVals[i]))
                self.sliders[i][j].sliderReleased.connect(self.updateSlider)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(1180, 40, 81, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(1140, 240, 161, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1370, 40, 101, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(1330, 240, 151, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(1160, 300, 101, 21))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(1140, 500, 241, 16))
        self.label_6.setObjectName("label_6")

        self.pattern = []
        for i in range(16):
            self.pattern.append(QtWidgets.QSpinBox(self.centralwidget))
            self.pattern[i].setGeometry(QtCore.QRect(160+50*i, 250, 31, 31))
            self.pattern[i].setObjectName("p" + str(i+1))
            self.pattern[i].setRange(0,4)
            self.pattern[i].valueChanged.connect(self.updateRunPattern)

        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(10, 250, 161, 20))
        self.label_7.setObjectName("label_7")

        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(10, 0, 341, 31))
        self.label_8.setObjectName("label_8")

        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(1110, 0, 261, 31))
        self.label_9.setObjectName("label_9")

        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(1080, 40, 21, 721))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(320, 50, 20, 181))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(380, 10, 681, 221))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)

        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(1330, 500, 241, 16))
        self.label_10.setObjectName("label_10")

        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(1350, 300, 121, 21))
        self.label_11.setObjectName("label_11")

        self.nPeriodInput = QtWidgets.QSpinBox(self.centralwidget)
        self.nPeriodInput.setGeometry(QtCore.QRect(1140, 590, 42, 22))
        self.nPeriodInput.setObjectName("nPeriodInput")
        self.nPeriodInput.setValue(4)

        self.homePosSetLabel = QtWidgets.QLabel(self.centralwidget)
        self.homePosSetLabel.setGeometry(QtCore.QRect(1140, 620, 300, 22))
        self.homePosSetLabel.setObjectName("baseVolumeSet")
        
        self.homePosInput = QtWidgets.QLineEdit(self.centralwidget)
        self.homePosInput.setGeometry(QtCore.QRect(1140, 650, 191, 21))
        self.homePosInput.setText("")
        self.homePosInput.setObjectName("homePosInput")
        self.homePosInput.setPlaceholderText(str(self.homePos))

        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(1140, 560, 221, 21))
        self.label_12.setObjectName("label_12")

        self.getPreload = QtWidgets.QPushButton(self.centralwidget)
        self.getPreload.setGeometry(QtCore.QRect(1140, 680, 200,30))
        self.getPreload.setObjectName("getPreload")

        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(1140, 720, 200,30))
        self.saveButton.setObjectName("saveButton")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1506, 18))
        self.menubar.setObjectName("menubar")

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        #Connect Components
        self.tableWidget.cellChanged[int,int].connect(self.tableChanged) 
        self.tidalVolumeInput.returnPressed.connect(self.updateTidalVolume)
        self.baseVolumeInput.returnPressed.connect(self.updateBaseVolume)
        self.rateInput.returnPressed.connect(self.updateRate)
        self.nPeriodInput.valueChanged[int].connect(self.updateNPeriods)
        self.getPreload.clicked.connect(self.loadPreset)
        self.saveButton.clicked.connect(self.saveConfig)
        self.homePosInput.returnPressed.connect(self.updatehomePos)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.rateLabel.setText(_translate("MainWindow", "Enter Breathing Rate (breaths per minute)"))
        self.tidalVolumeLabel.setText(_translate("MainWindow", "Enter Tidal Volume (mL)"))
        self.baseVolumeLabel.setText(_translate("MainWindow", "Enter Base Lung Volume (mL)"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Position</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "1       2      3      4"))
        self.label_3.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Velocity</span></p></body></html>"))
        self.label_4.setText(_translate("MainWindow", "1       2      3      4"))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Acceleration</span></p></body></html>"))
        self.label_6.setText(_translate("MainWindow", "1       2      3      4"))
        self.label_7.setText(_translate("MainWindow", "Position Sequence"))
        self.label_8.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Desired Respiratory Cycle Characteristics</span></p></body></html>"))
        self.label_9.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Actuator Move Characteristics</span></p></body></html>"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "Move 1"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "Move 2"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "Move 3"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "Move 4"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Position"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Velocity"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Acceleration"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Deceleration"))
        self.label_10.setText(_translate("MainWindow", "1       2      3      4"))
        self.label_11.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Deceleration</span></p></body></html>"))
        self.label_12.setText(_translate("MainWindow", "Number of Periods to Plot"))
        self.homePosSetLabel.setText(_translate("MainWindow", "Enter Actuator Home Position (mm)"))
        self.getPreload.setText(_translate("MainWindow", "Load Pre-Set Motion"))
        self.saveButton.setText(_translate("MainWindow", "Save Configuration"))

    def posToLungVol(self,pos):
        #Give position in mm, using the Tolomatic coordinate system
        # (90mm at full extension, 0mm at full retraction)
        return self.homeVol + self.pistonArea * (self.homePos - pos)/10

    def saveConfig(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self.centralwidget,"Save Current Configuration","","JSON Files (*.json)")
        if filename != None and filename[0] != '':
            order = [0]*len(self.pattern)
            for i in range(len(self.pattern)):
                order[i] = self.pattern[i].value()

            jsonDict = {"order": order}

            nMoves = 0
            moveDicts = []
            for mv in self.vals:
                nMoves += 1
                move = {"pos": mv[0], "vel": mv[1], "accel": mv[2], "decel": mv[3]}
                jsonDict["move" + str(nMoves)] = move

            jsonDict["nMoves"] = nMoves

            jsonString = json.dumps(jsonDict)

            with open(filename[0], 'w') as file:
                file.write(jsonString)

    def loadPreset(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget,"Choose Pre-Set Actuator Motion", "","JSON Files (*.json)")
        try:
            if filename != None and filename[0] != '':
                with open(filename[0]) as file:
                    preset = json.load(file)

                nMoves = int(preset["nMoves"])

                for i in range(nMoves):
                    if i < 4: #Currently only support 4 moves
                        move = preset["move" + str(i+1)]
                        self.vals[i][0] = float(move["pos"])
                        self.vals[i][1] = float(move["vel"])
                        self.vals[i][2] = float(move["accel"])
                        self.vals[i][3] = float(move["decel"])

                    for j in range(4): #pvad
                        self.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(self.vals[i][j])))

                order = preset["order"]
                for i in range(len(order)):
                    self.pattern[i].setValue(order[i])

        except:
            print("Failed to read JSON file. Ensure file is not corrupt, json is error free, and nMoves corresponds to the actual number of moves.")
                    
    def updateNPeriods(self, val):
        self.nt = float(val)
        self.dt = self.nt * self.T / self.N
        self.updatePlot()

    def waveform(self, t, A, f, m):
        #Create waveform with amplitude A (mL), frequency f (Hz), base value m (mL)

        #Create respiratory waveform with period 1/f, normalized between 0 and 1
        T = 1.0/f #Period
        n = len(t)
        N = t[-1] / T
        t = np.array((2*np.pi*f)*t)
        w = np.exp(-1.71668*t)*(0.0106 + 2.3313*t + 0.535*t**2 + 3.9594*t**3)/(2.3062 + 0.3517*t - 0.6487*t**2 + 0.1177*t**3)

        idx = int(n/N)

        i = idx+1
        while i + idx < n:
            w[i:i+idx] = w[:idx]
            i = i + idx + 1
        w[i:] = w[:n-i]

        #Scale and shift waveform to achieve desired mean value, and amplitude
        w *= A
        w += m
        return w

        # The data used to create this function:
        # t = [0, 0.024448, 0.079457, 0.14669, 0.18947, 0.24448, 0.29949, 0.3545, 0.42784, 0.49508, 0.56842, 0.64177, 
        #     0.70289, 0.78845, 0.85569, 0.94737, 1.0268, 1.1002, 1.1857, 1.2835, 1.3752, 1.4791, 1.5769, 1.6747, 1.7908, 
        #     1.907, 2.0536, 2.1576, 2.2859, 2.3959, 2.5182, 2.616, 2.7076,2.8177,2.946, 3.0682,3.1599,3.221, 3.2761, 3.3311, 
        #     3.4044, 3.4411, 3.49, 3.5328,3.5694,3.6061,3.6611,3.6978,3.7528,3.7895,3.8628,3.8812,3.9423,3.9912,4.0462,4.1012,
        #     4.1868,4.2662,4.3823,4.5046,4.639, 4.7491, 4.8652, 4.9997, 5.1158, 5.2502, 5.3847, 5.5008, 5.6231, 5.7942, 5.9409, 
        #     6.1059, 6.2832]
        # w = [0.0071599, 0.040573, 0.076372, 0.1074, 0.14558, 0.18138, 0.2148, 0.25537, 0.29594, 0.33413, 0.36516, 0.40095, 
        #     0.43914, 0.47017, 0.51313, 0.54893, 0.58234, 0.62053, 0.64916, 0.6969, 0.73508, 0.77327, 0.80907, 0.84487, 0.87112, 
        #     0.90215, 0.93317, 0.95704, 0.97136, 0.98091, 1, 0.99761, 0.99761, 0.99761, 0.98568, 0.96659, 0.93795, 0.90931, 
        #     0.87828, 0.84726, 0.8043, 0.77327, 0.74224, 0.6969, 0.66348, 0.6253, 0.57757, 0.53222, 0.49881, 0.45346, 0.41289, 
        #     0.38186, 0.35322, 0.31981, 0.28401, 0.25298, 0.22673, 0.1957, 0.16229, 0.13365, 0.11456, 0.10024, 0.085919, 0.076372, 
        #     0.064439, 0.047733, 0.042959, 0.0358, 0.02864, 0.019093, 0.01432, 0.0071599, 0]

    def updatePlot(self):
        self.t = np.linspace(0,self.nt/self.rate,self.N)
        self.v = self.waveform(self.t, A=self.tidalVolume, f=self.rate, m=self.baseVolume)
        
        self.plt.plot(self.t, self.v, pen='g', clear=True)
        self.plt.plot(self.tAct, self.vAct, pen='r')
        self.plt.setXRange(0,self.nt/self.rate)

    def tableChanged(self, row, col):
        #row = move number
        #col = parameter type (pos, vel, accel, decel)
        if self.dontUpdateTable:
            return

        #Make sure a number was actually entered
        try:
            float(self.tableWidget.item(row,col).text())
        except ValueError:
            return

        newNum = float(self.tableWidget.item(row,col).text())
        if newNum > self.maxVals[col]:
            newNum = 0
            self.dontUpdateTable = True #Avoid infinite recursion
            self.tableWidget.setItem(row,col,QtWidgets.QTableWidgetItem(str(newNum)))
            self.dontUpdateTable = False
        else:
            self.vals[row][col] = newNum
        
        self.sliders[col][row].setValue(int(newNum / self.maxVals[col] * 500))
        self.updateRunPattern()

    def updatehomePos(self):
        self.homePos = self.textInputHandler(self.homePosInput, self.homePosSetLabel, self.maxHomePos,
            self.minHomePos, self.defaultHomePos)
        self.homePosInput.setPlaceholderText(str(self.homePos))
        self.updateRunPattern()

    def updateSlider(self):
        self.dontUpdateTable = True
        for i in range(4): #pvad
            for j in range(4): #move number
                self.vals[j][i] = self.sliders[i][j].value() / 500.0 * self.maxVals[i]
                self.tableWidget.setItem(j,i,QtWidgets.QTableWidgetItem(str(self.vals[j][i])))

        self.dontUpdateTable = False
        self.updateRunPattern()

    def updateBaseVolume(self):
        self.baseVolume = self.textInputHandler(self.baseVolumeInput, self.baseVolumeLabel, self.maxBaseVolume,
            self.minBaseVolume, self.defaultBaseVolume)
        self.homeVol = self.baseVolume
        self.baseVolumeInput.setPlaceholderText(str(self.baseVolume))
        self.updatePlot()

    def updateTidalVolume(self):
        self.tidalVolume = self.textInputHandler(self.tidalVolumeInput, self.tidalVolumeLabel, self.maxTidalVolume,
            self.minTidalVolume, self.defaultTidalVolume)
        self.tidalVolumeInput.setPlaceholderText(str(self.tidalVolume))
        self.updatePlot()

    def updateRate(self):
        self.rate = self.textInputHandler(self.rateInput, self.rateLabel, self.maxRate,
            self.minRate, self.defaultRate) / 60.0
        self.rateInput.setPlaceholderText(str(self.rate*60))
        self.T = 1.0/self.rate
        self.dt = self.nt * self.T / self.N
        self.updatePlot()

    def textInputHandler(self, textInput, label, maxVal, minVal, defaultVal):
        try:
            storeVal = float(textInput.text())
        except ValueError:
            label.setStyleSheet('color: red')

        if storeVal > maxVal or storeVal < minVal:
            storeVal = defaultVal
            label.setStyleSheet('color: red')
        else:
            label.setStyleSheet('color: green')

        textInput.clear()
        return storeVal

    def updateRunPattern(self):

        for i in range(16):
            idx = self.pattern[i].value() - 1
            if idx == -1: #Pattern not set yet here
                self.runPattern[i] = [self.homePos,30,254,254]
            else:
                self.runPattern[i] = [self.vals[idx][j] for j in range(4)]

        self.updateCurve()

    def updateCurve(self):
        #Position Velocity Acceleration Deceleration
        p = np.zeros(1)
        t = np.zeros(1)
        v0 = 0
        p[0] = self.runPattern[0][0]

        for i in range(1,len(self.runPattern)):
            move = self.runPattern[i]
            ti, pi, vi = self.simulateOneMove(p[-1], move[0], move[1], move[2], move[3], self.dt, t[-1], v0)
            v0 = vi[-1]
            p = np.concatenate((p,pi))
            t = np.concatenate((t,ti))

        self.tAct = t
        self.vAct = self.posToLungVol(p)
        self.updatePlot()

    def simulateOneMove(self, p0, pf, vel, accel, decel, dt, t0 = 0, v0=0):
        #Simulate one period
        #p0 starting position in mm
        #pf goal position in mm (position input to TMI)
        #vel goal maximum velocity (velocity input to TMI)
        #accel acceleration (acceleration input to TMI)
        #decel decelaration (input to TMI)
        #t0 start time
        #v0 starting velocity

        #Accel, decel, vel are given as absolute. Adjust depending on direction
        if pf < p0:
            vel *= -1
            accel *= -1
        else:
            decel *= -1

        t = [t0]
        p = [p0]
        v = [v0]

        while self.endCondition(p0,pf,p[-1]): #Go until we reach goal position
            if abs(v[-1]) >= abs(vel): 
                #If we have reached goal velocity, stop accelerating
                accel = 0

                if np.sign(v[-1]) != np.sign(pf-p[-1]):
                    #We have stopped accelerating but are going in the wrong direction. 
                    #Something went wrong. Integration will diverge and loop infinitely
                    print('NUMERICAL INTEGRATION DIVERGENT. STOPPED INTEGRATION')
                    break
            if decel != 0 and self.willOvershoot(v[-1],0,p[-1],pf,decel):
                #If we wish to decelerate to 0 at pf, check that this is still possible
                #at current position and speed. If not, immediately start decelerating
                accel = decel

            t += [t[-1]+dt]
            v += [v[-1]+accel*dt]
            p += [p[-1]+(v[-1]+v[-2])/2*dt]

        return np.array(t), np.array(p), np.array(v)
    
    def endCondition(self, p0, pf, pCurr):
        if p0 < pf:
            return pCurr < pf;
        else:
            return pCurr > pf;
    
    def willOvershoot(self, v0, vF, x0, xF, a):
        #v0 current speed
        #x0 current position
        #xF final (goal) position we are trying not to overshoot
        #a deceleration

        if (a>0 and v0 > 0) or (a<0 and v0<0):
            #Due to some small errors, v will not always be identically zero when we think
            #it has changed direction, which leads to weird results, so just ignore this case
            return False
        elif a < 0:
            return (vF**2-v0**2) / (2*a) + x0 > xF
        else:
            return (vF**2-v0**2) / (2*a) + x0 < xF

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
