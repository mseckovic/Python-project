from PySide2 import QtWidgets, QtCore, QtGui
from ...sqlite_init import konekcija_ka_bazi

class DodajHaluUMagacinDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        #iteracija kroz tipove hala iz baze za potrebe izbora korisnika --------
        self._conn = konekcija_ka_bazi()
        self._c = self._conn.cursor()
        self._c = self._conn.execute("SELECT naziv_hale, tip_hale_id FROM tip_hale" )
        self.lista_hala_db = list(self._c.fetchall())
        self._conn.commit()
        tmpList = []
        for item in self.lista_hala_db:
            tmpList.append(item[0])
        self.tipHaleID  = "" #izabrana hala
        #kraj iteracije kroz bazu ----------------------------------------------

        self.setWindowTitle("Dodaj halu u magacin")

        self.vbox_layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.naziv_hale_input = QtWidgets.QLineEdit(self)
        self.tip_hale_combobox = QtWidgets.QComboBox(self)
        self.ukupan_br_mesta_input = QtWidgets.QLineEdit(self)

        #stavljamo vrednosti u tip hale dropdown
        self.tip_hale_combobox.addItems(tmpList)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
            | QtWidgets.QDialogButtonBox.Cancel, parent=self)

        self.form_layout.addRow("Naziv Hale:", self.naziv_hale_input)
        self.form_layout.addRow("Tip Hale:", self.tip_hale_combobox)
        self.form_layout.addRow("Ukupan Broj Mesta:", self.ukupan_br_mesta_input)

        self.vbox_layout.addLayout(self.form_layout)
        self.vbox_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)

        self.setLayout(self.vbox_layout)

    def _on_accept(self):
        if self.naziv_hale_input.text() == "":
            QtWidgets.QMessageBox.warning(self,
            "Provera Naziva Hale", "Naziva Hale mora biti popunjen!", QtWidgets.QMessageBox.Ok)
            return
        if self.ukupan_br_mesta_input.text().lstrip("0").strip() == "":
            QtWidgets.QMessageBox.warning(self,
            "Provera ukupnog br mesta", "Ukupan broj mesta ne sme biti prazan!", QtWidgets.QMessageBox.Ok)
            return

        temp_input = self.ukupan_br_mesta_input.text().lstrip("0").strip()
        if self.da_li_je_int(temp_input):
            temp_input = int(temp_input)
            lenInt = len(str(temp_input))
            if temp_input <= 0:
                QtWidgets.QMessageBox.warning(self,
                "Ukupan Broj Mesta", "Broj Mesta mora biti veći od nule!", QtWidgets.QMessageBox.Ok)
                return
        else:
            QtWidgets.QMessageBox.warning(self,
            "Ukupan Broj Mesta2", "Morate uneti brojčanu vrednost!", QtWidgets.QMessageBox.Ok)
            return

        izabranINDEX = self.tip_hale_combobox.currentIndex()
        self.tipHaleID  = self.lista_hala_db[izabranINDEX][1]

        self.accept()
    def get_data(self):
        return {
            "nazivHale": self.naziv_hale_input.text(),
            "tipHaleID": self.tipHaleID,
            "brMesta": self.ukupan_br_mesta_input.text().lstrip("0").strip()
        }

    def da_li_je_int(self, input):
        try:
            num = int(input)
        except ValueError:
            return False
        return True
