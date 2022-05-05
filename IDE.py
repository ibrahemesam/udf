class IDE(QWidget):
    def __init__(self):
        # todo: override os.exit to execute some functions before it && and save inp_exec (encapsule IDE class)
        super().__init__()
        from PyQt5 import uic
        uic.loadUi(f"{g.mPath}/app/IDE.ui", self)
        self.btn_exec.clicked.connect(lambda: self.test_exec(self.inp_exec.toPlainText().strip().replace('\t', '    ')))
        shortcut('F4', self, lambda: self.test_exec(self.inp_exec.toPlainText().strip().replace('\t', '    ')), 0)
        shortcut('F5', self, lambda: self.test_exec(open('dev-exec.py').read().replace('\t', '    ')), 0)
        global cout
        def cout(st):
            self.tabs.setCurrentIndex(2)
            self.tabs_tests.setCurrentIndex(1)
            self.inp_exec_out.setPlainText(str(st))
        try:
            self.inp_exec.setPlainText(my.fileRead('Data/exec.py'))
            self.inp_exec_out.setPlainText(my.fileRead('Data/exec_out.py'))
        except: pass
        import syntax
        self.inp_exec.setStyleSheet("""QPlainTextEdit{
                font-family:'Consolas'; 
                color: #ccc; 
                background-color: #2b2b2b;}""")
        self.highlight1 = syntax.PythonHighlighter(self.inp_exec.document())
        self.inp_exec_out.setStyleSheet("""QPlainTextEdit{
                font-family:'Consolas'; 
                color: #ccc; 
                background-color: #2b2b2b;}""")
        self.highlight2 = syntax.PythonHighlighter(self.inp_exec_out.document())
        #todo setInterval to save test code and output to the db file
        def saveTestCode():
            global exec_code; exec_code = self.inp_exec.toPlainText()
            while True:
                if self.inp_exec.toPlainText() != exec_code:
                    my.fileWrite('Data/exec.py', self.inp_exec.toPlainText())
                    my.fileWrite('Data/exec_out.py', self.inp_exec_out.toPlainText())
                    exec_code = self.inp_exec.toPlainText()
                wait(5000)
        qthread_task(lambda: saveTestCode()).start()

    def test_exec(self, code):
        try: exec(code)
        except:
            #try: g.msg(str(sys.exc_info()[1]))
            try: g.msg(traceback.format_exc())
            except: g.msg("Can't get the error ]:")

