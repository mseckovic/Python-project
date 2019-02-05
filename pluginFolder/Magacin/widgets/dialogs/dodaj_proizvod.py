from PySide2 import QtWidgets, QtCore, QtGui

class DodajProizvodDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setWindowTitle("Dodaj proizvod")
        self.vbox_layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.naziv_p_input = QtWidgets.QLineEdit(self)
        self.rok_upotrebe_input = QtWidgets.QDateEdit(self)
        self.temp_cuvanja_input = QtWidgets.QLineEdit(self)
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
            | QtWidgets.QDialogButtonBox.Cancel, parent=self)

        self.rok_upotrebe_input.setDate(QtCore.QDate.currentDate())
        self.rok_upotrebe_input.setCalendarPopup(True)
        self.form_layout.addRow("Naziv Proizvoda:", self.naziv_p_input)
        self.form_layout.addRow("Rok Upotrebe:", self.rok_upotrebe_input)
        self.form_layout.addRow("Temperatura Čuvanja:", self.temp_cuvanja_input)

        self.vbox_layout.addLayout(self.form_layout)
        self.vbox_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)

        self.setLayout(self.vbox_layout)

    def _on_accept(self):

        #provera da naziv proizvoda nije prazan tekst
        if self.naziv_p_input.text() == "":
            QtWidgets.QMessageBox.warning(self,
            "Provera imena", "Ime mora biti popunjeno!", QtWidgets.QMessageBox.Ok)
            return
        #provera da rok upotrebe: nije prazan tekst
        #                         je izmedju -10 i 100 (stepeni)
        if self.rok_upotrebe_input.text() == "":
            QtWidgets.QMessageBox.warning(self,
            "Provera prezimena", "Prezime mora biti popunjeno!", QtWidgets.QMessageBox.Ok)
            return
        temp_input = self.temp_cuvanja_input.text().strip().lstrip("0").strip()
        if self.da_li_je_int(temp_input):
            temp_input = int(temp_input)
            if (temp_input > 100) or (temp_input < -10): #if (temp_input <=100) and (temp_input >=-10):
                QtWidgets.QMessageBox.warning(self,
                "Provera temperature", "Tremperatura mora biti između -10 i 100 stepeni!", QtWidgets.QMessageBox.Ok)
                return
        else:
            QtWidgets.QMessageBox.warning(self,
            "Ukupan Broj Mesta2", "Morate uneti brojčanu vrednost!", QtWidgets.QMessageBox.Ok)
            return
        self.accept()
    def get_data(self):

        return {
            "nazivP": self.naziv_p_input.text(),
            "rokUpotrebe": self.rok_upotrebe_input.text(),
            "temp": self.temp_cuvanja_input.text().lstrip("0").strip()
        }

    def da_li_je_int(self, input):
        try:
            num = int(input)
        except ValueError:
            return False
        return True
