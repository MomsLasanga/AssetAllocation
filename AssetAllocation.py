"""
Asset Allocation
By Patrick Murrell
Created 6/17/2020

This program that takes a csv positions file from fidelity.com from a Roth IRA account that contains the
investments of SPAXX, FXNAX, FZILX, and FZROX. Since SPAXX is a Money Market fund then it is assumed that the money in
here is not meant to be calculated in the total asset allocation of the account.

Once the csv file is entered its data is scraped using the csv python library and the data used in calculations and
tables that display useful statistics to the user. The user then should enter the amount they want to invest, and then
click the "Calculate Investment Strategy" button to generate a table of values and display the recommended investment
strategy on three buttons. These three buttons tell us whether to buy or sell or hold a dollar amount of each
fund. Clicking these buttons copy their number values to the clip board to make the buying and selling of stocks easier

This is a program written ideally for a single user (my investment strategy), but anyone can use the code in order to
build their own version if they want.
"""
import csv  # for the scraping of the csv file
import re  # for making sure we just copy the buttons numbers
from PyQt5.QtWidgets import QFileDialog  # to use the file browser in order to select a fidelity issued csv file
from PyQt5 import QtCore, QtWidgets, QtGui  # to build the applications GUI
import sys  # for starting and exiting the application


# noinspection PyBroadException
class UiMainWindow(object):

    # decides whether or not we buy/sell/hold the current allocation of a fund
    def buy_or_sell(self, percentage, total, current, money_to_invest, key):
        s: str  # the string we print onto the buttons
        target = total * percentage  # our ideal dollar amount invested in the fund
        actual_vs_target_ratio = target / current  # the ratio of the ideal target allocation and the current allocation

        # if the fund is 5% outside of its target allocation and we are putting in/taking out new money then we
        # adjust the fund
        if .95 < actual_vs_target_ratio < 1.05 and int(money_to_invest) == 0:
            s = "Looks good for "
        else:  # buy or sell the exact amount of the fund so we hit the target allocation
            amount_to_trade = str(round(abs(current - target), 2))
            if actual_vs_target_ratio > 1.0:
                s = "Buy "
            else:
                s = "Sell "
            s += "$" + amount_to_trade + " "
        self.target_value.append(str(round(target, 2)))  # so we can display the target value in the info table
        s += self.info_table[1][key]  # add the name of the investment to the string
        return s  # return the text to add to the button

    # uses pandas to read from a csv file and add the current balances of investments to list
    def scrape_values_from_csv(self):
        temp_names = []  # temporarily stores labels of funds
        temp_balances = []  # temporarily stores current balances of funds
        csv_list = []  # list that stores the contents of the csv file
        self.current_balances.clear()  # clear the list of balances so we can replace them with the current csv values

        try:  # import the list from Fidelity using pandas
            with open(self.filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:  # read the csv file contents into a list
                    csv_list.append(row)
        except:  # if this doesn't work we just notify the user by returning a list of -1 (a flag of sorts)
            self.current_balances = [-1]  # we check this to report that they did not enter a correct csv file
        else:
            # reset the info table list and set its values to the headings
            self.info_table = [['Symbol', 'Current Value', 'Current Allocation', 'Target value', 'Target Allocation']]
            for i in range(2, 5):  # read through the csv list
                temp_balances.append(csv_list[i][6])  # access the current values
                self.current_balances.append(float(temp_balances[i - 2].replace('$', '')))  # remove the '$' sign
                temp_names.append(csv_list[i][1])  # add the name of the fund to label names
            self.info_table.append(temp_names)  # add the names and balances lists to the
            self.info_table.append(temp_balances)  # info table list

    # takes values from csv list, money we want to invest, and
    def calculate_strategy(self, money_to_invest):

        # Fixed Asset Allocation Percentages based on age/year of user (mine is set to every 20XX year, because I was
        # born in 1999)
        if "2020" in self.filename:
            bond_percentage = .2
            international_index_percentage = .3
            national_index_percentage = .5
        elif "2030" in self.filename:
            bond_percentage = .3
            international_index_percentage = .27
            national_index_percentage = .43
        elif "2040" in self.filename:
            bond_percentage = .4
            international_index_percentage = .23
            national_index_percentage = .37
        elif "2050" in self.filename:
            bond_percentage = .5
            international_index_percentage = .19
            national_index_percentage = .31
        elif "2060" in self.filename:
            bond_percentage = .6
            international_index_percentage = .15
            national_index_percentage = .25
        elif "2070" in self.filename:
            bond_percentage = .7
            international_index_percentage = .11
            national_index_percentage = .19
        elif "2080" in self.filename:
            bond_percentage = .8
            international_index_percentage = .08
            national_index_percentage = .12
        elif "2090" in self.filename:
            bond_percentage = .9
            international_index_percentage = .04
            national_index_percentage = .06
        else:
            bond_percentage = 1.0
            international_index_percentage = 0.0
            national_index_percentage = 0.0

        total_amount = money_to_invest + sum(self.current_balances)  # total current amount of money to be invested

        self.target_value.clear()  # clear the target values list

        # updates the buttons to display the recommended asset allocation to the user
        self.bonds_button.setText(self._translate("main_window", self.buy_or_sell(  # set bonds button text
            bond_percentage, total_amount, self.current_balances[0], money_to_invest, 0)))
        self.international_button.setText(self._translate("main_window", self.buy_or_sell(  # set international button
            international_index_percentage, total_amount, self.current_balances[1], money_to_invest, 1)))
        self.national_button.setText(self._translate("main_window", self.buy_or_sell(  # set national button text
            national_index_percentage, total_amount, self.current_balances[2], money_to_invest, 2)))
        # add current allocation, ideal fund balances, and ideal allocation of account to info table list
        self.info_table.append([str(round(100 * self.current_balances[0] / (total_amount - money_to_invest), 2)) + "%",
                                str(round(100 * self.current_balances[1] / (total_amount - money_to_invest), 2)) + "%",
                                str(round(100 * self.current_balances[2] / (total_amount - money_to_invest), 2)) + "%"])
        self.info_table.append(self.target_value)
        self.info_table.append([str(100 * bond_percentage) + "%", str(100 * international_index_percentage) + "%",
                                str(100 * national_index_percentage) + "%"])

    # this method sets up the ui as well as a couple of variables used accross the program
    def __init__(self, main_win):
        button_stylesheet = "background-color: #3F3F3F; color: #ffffff"  # style sheet
        self.info_table = []  # table of investment information and positions we print out to the user
        self.current_balances = [-1]  # current balances tracks the list of fund balances pulled from the csv file
        self.numbers = re.compile(r'\d+(?:\.\d+)?')  # regular expression that is used to copy the button text numbers
        self.target_value = []  # stores the ideal balance values for each fund
        self.filename = ''  # name path of csv file is stored here
        self._translate = QtCore.QCoreApplication.translate  # shortened function name for ease of use

        # UI related code generated by PyQt file
        main_win.setObjectName("main_window")
        main_win.resize(780, 350)
        main_win.setAutoFillBackground(True)
        main_win.setStyleSheet("background-color: #4a4a4a; color: #ffffff; font: 10pt 'Consolas'")
        self.central_widget = QtWidgets.QWidget(main_win)
        self.central_widget.setAutoFillBackground(True)
        self.central_widget.setObjectName("central_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.central_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_vlayout = QtWidgets.QVBoxLayout()
        self.main_vlayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.main_vlayout.setContentsMargins(5, 5, 5, 5)
        self.main_vlayout.setSpacing(5)
        self.main_vlayout.setObjectName("main_vlayout")
        self.entry_hlayout = QtWidgets.QHBoxLayout()
        self.entry_hlayout.setContentsMargins(5, 5, 5, 5)
        self.entry_hlayout.setSpacing(5)
        self.entry_hlayout.setObjectName("entry_hlayout")
        self.entry_label = QtWidgets.QLabel(self.central_widget)
        self.entry_label.setObjectName("entry_label")
        self.entry_hlayout.addWidget(self.entry_label)
        self.entry_lineEdit = QtWidgets.QLineEdit(self.central_widget)
        self.entry_lineEdit.setObjectName("entry_lineEdit")
        self.entry_hlayout.addWidget(self.entry_lineEdit)
        spacer_item = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.entry_hlayout.addItem(spacer_item)
        self.main_vlayout.addLayout(self.entry_hlayout)
        self.two_button_horizontal = QtWidgets.QHBoxLayout()
        self.two_button_horizontal.setContentsMargins(5, 5, 5, 5)
        self.two_button_horizontal.setSpacing(5)
        self.two_button_horizontal.setObjectName("two_button_horizontal")
        self.csv_button = QtWidgets.QPushButton(self.central_widget)
        self.csv_button.setObjectName("csv_button")
        self.csv_button.setStyleSheet(button_stylesheet)
        self.csv_button.clicked.connect(self.open_csv)  # when csv button is clicked run the open csv method
        self.two_button_horizontal.addWidget(self.csv_button)
        self.calculate_button = QtWidgets.QPushButton(self.central_widget)
        self.calculate_button.setStyleSheet(button_stylesheet)
        self.calculate_button.setObjectName("calculate_button")
        self.calculate_button.clicked.connect(self.calculate)  # when the calculate button is clicked run calculate()
        self.two_button_horizontal.addWidget(self.calculate_button)
        self.main_vlayout.addLayout(self.two_button_horizontal)
        self.error_vlayout = QtWidgets.QVBoxLayout()
        self.error_vlayout.setContentsMargins(5, 5, 5, 5)
        self.error_vlayout.setSpacing(5)
        self.error_vlayout.setObjectName("error_vlayout")
        self.error_label = QtWidgets.QLabel(self.central_widget)
        self.error_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.error_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.error_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setObjectName("error_label")
        self.info_label = QtWidgets.QLabel(self.central_widget)
        self.info_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.info_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.info_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_label.setObjectName("error_label")
        self.error_vlayout.addWidget(self.info_label)
        self.error_vlayout.addWidget(self.error_label)
        self.main_vlayout.addLayout(self.error_vlayout)
        self.three_button_horizontal = QtWidgets.QHBoxLayout()
        self.three_button_horizontal.setContentsMargins(5, 5, 5, 5)
        self.three_button_horizontal.setSpacing(5)
        self.three_button_horizontal.setObjectName("three_button_horizontal")
        self.bonds_button = QtWidgets.QPushButton(self.central_widget)
        self.bonds_button.setObjectName("bonds_button")
        self.bonds_button.setStyleSheet(button_stylesheet)
        self.bonds_button.clicked.connect(self.copy_bond_number)
        self.three_button_horizontal.addWidget(self.bonds_button)
        self.international_button = QtWidgets.QPushButton(self.central_widget)
        self.international_button.setObjectName("international_button")
        self.international_button.setStyleSheet(button_stylesheet)
        self.international_button.clicked.connect(self.copy_international_number)
        self.three_button_horizontal.addWidget(self.international_button)
        self.national_button = QtWidgets.QPushButton(self.central_widget)
        self.national_button.setObjectName("national_button")
        self.national_button.setStyleSheet(button_stylesheet)
        self.national_button.clicked.connect(self.copy_national_number)
        self.three_button_horizontal.addWidget(self.national_button)
        self.main_vlayout.addLayout(self.three_button_horizontal)
        self.verticalLayout_2.addLayout(self.main_vlayout)
        main_win.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(main_win)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 884, 21))
        self.menubar.setObjectName("menubar")
        main_win.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_win)
        self.statusbar.setObjectName("statusbar")
        main_win.setStatusBar(self.statusbar)
        self.reanimate_ui(main_win)
        QtCore.QMetaObject.connectSlotsByName(main_win)

    # Ui function that sets initial ui text
    def reanimate_ui(self, main_w):
        main_w.setWindowTitle(self._translate("main_window", "Asset Allocation"))
        self.entry_label.setText(self._translate("main_window", "The amount you want to invest:"))
        self.csv_button.setText(self._translate("main_window", "Browse For CSV"))
        self.calculate_button.setText(self._translate("main_window", "Calculate Investment Strategy"))
        self.error_label.setText(self._translate("main_window", ""))
        self.info_label.setText(self._translate("main_window", ""))
        self.bonds_button.setText(self._translate("main_window", ""))
        self.international_button.setText(self._translate("main_window", ""))
        self.national_button.setText(self._translate("main_window", ""))

    # creates a file explorer dialog to select csv. checks and reports if a valid csv was selected
    def open_csv(self):
        # open and select file from csv button
        filename_list = list(QFileDialog.getOpenFileName(main_window, 'Open file', "/", "csv files (*.csv)"))
        self.filename = str(filename_list[0])
        self.scrape_values_from_csv()
        if self.current_balances == [-1]:  # if a csv file is not detected
            self.csv_file_error()  # report an error to the user
        else:
            self.error_label.setText(self._translate("main_window", self.filename))  # show the file name to the user

    # check to make sure the user entered either a number or nothing, also entered a csv, then run calculate_strategy()
    def calculate(self):
        try:
            amount_to_invest = float(self.entry_lineEdit.text())  # check to see if the user entered a proper number
        except:
            if self.entry_lineEdit.text() == '':  # if the user enters nothing assume they are investing $0.00
                amount_to_invest = 0.00
            else:  # since the user did not enter a number throw an error and exit the function
                self.error_label.setText(self._translate("main_window", "You did not enter a valid amount"))
                return
        if self.current_balances != [-1]:  # if the user entered a valid csv
            self.calculate_strategy(amount_to_invest)  # calculate our strategy and fill the rest of the info table list
            self.error_label.setText(self._translate("main_window", "Strategy Calculated"))
            # print our info table list onto the screen in the form of a table
            s = 'Values From CSV: \n\n|'  # create the info table in a string called s
            for i in range(len(self.info_table[0])):
                s += "{:20}|".format((str(self.info_table[0][i]).ljust(15)))
            s += "\n" + "-" * int((len(s) * .85))
            for i in range(len(self.info_table[1])):
                s += "\n|"
                for j in range(1, len(self.info_table)):
                    s += "{:20}|".format((str(self.info_table[j][i]).ljust(15)))
            s += '\n'
            self.info_label.setText(self._translate("main_window", s))  # set the info label to the info table
            for i in range(3):  # remove last three values of info table list so they do not overlap with themselves
                self.info_table.remove(self.info_table[len(self.info_table) - 1])
        else:
            self.csv_file_error()  # report an error to the user

    # methods that copy the text of how much to buy/sell/hold from button onto clipboard
    def copy_bond_number(self):
        cb.setText(''.join(self.numbers.findall(self.bonds_button.text())), mode=cb.Clipboard)

    def copy_national_number(self):
        cb.setText(''.join(self.numbers.findall(self.national_button.text())), mode=cb.Clipboard)

    def copy_international_number(self):
        cb.setText(''.join(self.numbers.findall(self.international_button.text())), mode=cb.Clipboard)

    # report an error if a csv file is not detected (when self.current_values == [-1])
    def csv_file_error(self):
        self.error_label.setText(self._translate("main_window", "you did not enter a csv file"))


# main function that starts and closes the app
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    cb = QtWidgets.QApplication.clipboard()
    cb.clear(mode=cb.Clipboard)
    ui = UiMainWindow(main_window)
    main_window.show()
    sys.exit(app.exec_())
