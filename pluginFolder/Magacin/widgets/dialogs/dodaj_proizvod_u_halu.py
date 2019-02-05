from PySide2 import QtWidgets, QtCore, QtGui
from ...sqlite_init import konekcija_ka_bazi

class DodajProizvodUHaluDialog(QtWidgets.QDialog):

    def __init__(self, parent=None , nazivHale=None , halaID=None):

        super().__init__(parent)
        self.this_naziv_hale = nazivHale
        self.this_halaID = halaID

        #iteracija kroz bazu ---------------------------------------------------

        #rashlladne_hale GET
        self._conn = konekcija_ka_bazi()
        self._c = self._conn.cursor()
        # proizvodi list GET
        self.proizvodi_db_list = self.loop_db_get_element_list("SELECT naziv_proizvoda, proizvodi_id, temp_cuvanja  FROM proizvodi")
        self.proizvodi_out_list = self.loop_list_tuple_to_normal_list(self.proizvodi_db_list)
        #kraj iteracije kroz bazu ----------------------------------------------
        self.proizvodID_izabran = ""
        self.izabran_proizvod_ime = ""
        self.nov_br_zauzetih_mesta = ""

        self.setWindowTitle("Dodaj proizvod u halu")
        self.resize(250, 180)
        self.vbox_layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.hala_label = QtWidgets.QLabel(self)
        self.proizvod_combobox = QtWidgets.QComboBox(self)
        self.kolicina_input = QtWidgets.QLineEdit(self)

        #self.hala_input.addItems(self.tip_hale_out_list)
        self.proizvod_combobox.addItems(self.proizvodi_out_list)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok
            | QtWidgets.QDialogButtonBox.Cancel, parent=self)

        self.hala_label.setText(self.this_naziv_hale)
        self.form_layout.addRow("Hala:", self.hala_label)
        self.form_layout.addRow("Proizvod:", self.proizvod_combobox)
        self.form_layout.addRow("Količina:", self.kolicina_input)


        self.vbox_layout.addLayout(self.form_layout)
        self.vbox_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)

        self.setLayout(self.vbox_layout)

    def loop_db_get_element_list(self, stringSELECT):
        self._c = self._conn.cursor()
        self._c = self._conn.execute(stringSELECT)
        return list(self._c.fetchall())

    def loop_list_tuple_to_normal_list(self, listFETCH):
        returnLIST = []
        for item in listFETCH:
            returnLIST.append(item[0])
        return returnLIST

    def _on_accept(self):

        temp_input = self.kolicina_input.text().lstrip("0").strip()
        if self.da_li_je_int(temp_input):
            temp_input = int(temp_input)
            if (temp_input < 0): #if (temp_input <=100) and (temp_input >=-10):
                QtWidgets.QMessageBox.warning(self,
                "Provera količine", "Količina treba biti veća od 0", QtWidgets.QMessageBox.Ok)
                return
        else:
            QtWidgets.QMessageBox.warning(self,
            "Provera količine2", "Morate uneti brojčanu vrednost!", QtWidgets.QMessageBox.Ok)
            return

        # kolicina rashladne_hale i kolicina proizvoda
        result = self._conn.execute("SELECT ukupan_br_mesta, br_zauzetih_mesta FROM rashladne_hale WHERE rashladne_hale_id = :halaid" ,{'halaid' : self.this_halaID} )
        mestaHale = list(result.fetchall())
        ukpno_mesta =  int(mestaHale[0][0])
        br_zauzetih_mesta = int(mestaHale[0][1])
        self.nov_br_zauzetih_mesta = br_zauzetih_mesta + int(temp_input)
        if (  self.nov_br_zauzetih_mesta > ukpno_mesta ):
            QtWidgets.QMessageBox.warning(self,
            "Provera količine3", "Količina mora biti jednaka ili manja od ukupnog broja raspoloživog mesta!", QtWidgets.QMessageBox.Ok)
            return

        #provera da li se temperatura poklapa-----------------------------------
        #temperatura od tipa - hale
        result = self._conn.execute("SELECT tip_hale.min_temp , tip_hale.max_temp FROM rashladne_hale INNER JOIN tip_hale ON rashladne_hale.tip_hale_id = tip_hale.tip_hale_id WHERE rashladne_hale_id = :halaid" ,{'halaid' : self.this_halaID} )
        temp_hale = list(result.fetchall())
        min_temp_hale = int(temp_hale[0][0])
        max_temp_hale = int(temp_hale[0][1])
        #temperatura - proizvoda
        izabranINDEX = self.proizvod_combobox.currentIndex()
        temp_proizvoda  = self.proizvodi_db_list[izabranINDEX][2]

        if (temp_proizvoda < min_temp_hale ) or (temp_proizvoda > max_temp_hale ):
            QtWidgets.QMessageBox.warning(self,
            "Provera temperature", "Temperatura proizvoda ne odgovara hali!", QtWidgets.QMessageBox.Ok)
            return

        self.proizvodID_izabran  = self.proizvodi_db_list[izabranINDEX][1]
        self.izabran_proizvod_ime = self.proizvodi_db_list[izabranINDEX][0]
        self.accept()
    def get_data(self):

        return {
            "halaID": self.this_halaID,
            "proizvodID": self.proizvodID_izabran,
            "kolicina": self.kolicina_input.text().lstrip("0").strip(),
            "nazivProizvoda" : self.izabran_proizvod_ime,
            "novBrZauzetih" : self.nov_br_zauzetih_mesta
        }

    def da_li_je_int(self, input):
        try:
            num = int(input)
        except ValueError:
            return False
        return True
