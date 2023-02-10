from __future__ import print_function
import nuke

from Qt import QtWidgets, QtGui, QtCore, QtOpenGL

# https://www.pixelmania.se/fixing-an-annoying-nuke-feature/


class MouseEventGrabber(QtCore.QObject):
    def __init__(self):
        super(MouseEventGrabber, self).__init__()
        self.middleclicked = False
        self.clickpos = None
        self.app = QtWidgets.QApplication.instance()
        dags = [widget for widget in self.app.allWidgets() if widget.windowTitle() == "Node Graph"]
        if dags:
            self.dag = None
            if dags[0].size().height() > dags[1].size().height():
                self.dag = dags[1].findChild(QtOpenGL.QGLWidget)
            else:
                self.dag = dags[0].findChild(QtOpenGL.QGLWidget)
            if self.dag:
                print("Installing DAG event filter")
                self.dag.installEventFilter(self)
        if not dags or not self.dag:
            print("Couldn't install event filter, DAG not found")
    
    def eventFilter(self, widget, event):
        '''Grab mouse and key events.'''
        if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.middleclicked = True
            self.clickpos = QtGui.QCursor.pos()
            #print("Set middle clicked: True (position: %d, %d)" % (self.clickpos.x(), self.clickpos.y()))
        if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.MouseButton.MiddleButton and self.middleclicked:
            newpos = QtGui.QCursor.pos()
            #print("Set middle clicked: False (position: %d, %d)" % (newpos.x(), newpos.y()))
            self.middleclicked = False
            if newpos.x() > self.clickpos.x() - 5 and newpos.x() < self.clickpos.x() + 5 and newpos.y() > self.clickpos.y() - 5 and newpos.y() < self.clickpos.y() + 5:
                # print("Blocked zoom out from middleclick")
                import nukescripts
                nukescripts.clear_selection_recursive()
                dot = nuke.createNode("Dot", inpanel=False)
                self.app = QtWidgets.QApplication.instance()
                dags = [widget for widget in self.app.allWidgets() if widget.windowTitle() == "Node Graph"]
                if dags:
                    self.dag = None
                    if dags[0].size().height() > dags[1].size().height():
                        self.dag = dags[1].findChild(QtOpenGL.QGLWidget)
                    else:
                        self.dag = dags[0].findChild(QtOpenGL.QGLWidget)
                QtWidgets.QApplication.sendEvent(self.dag, QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress, self.dag.mapFromGlobal(newpos), QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier))
                nuke.delete(dot)
                return True
        return False


def SetupEventFilter():
    global mouseEventFilter
    if not "mouseEventFilter" in globals():
        mouseEventFilter = MouseEventGrabber()

nuke.addOnScriptLoad(SetupEventFilter)