from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt
from ...modeli.svi_proizvodi_model import SviProizvodiListModel
from .dodaj_proizvod import DodajProizvodDialog
from ...sqlite_init import konekcija_ka_bazi

class AddPregledSvihProizvodaDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)
        #konekcija ka bazi podataka - sqlite #####################################
        self._conn = konekcija_ka_bazi()
        self._c = self._conn.cursor()
        ###########################################################################
        self.setWindowTitle("Pregled Svih Proizvoda")
        self.resize(700, 550)

        self.proizvod_options_layout = QtWidgets.QHBoxLayout()

        self.dodaj_proizvod = QtWidgets.QPushButton(QIcon("resources/icons/plus.png"), "Dodaj Proizvod")
        self.ukloni_proizvod = QtWidgets.QPushButton(QIcon("resources/icons/minus.png"), "Ukloni proizvod")
        self.plugin_proizvodi_layout = QtWidgets.QVBoxLayout()

        self.table_view = QtWidgets.QTableView(self)
        self._prikaz_svih_proizvoda_iz_baze()
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.proizvod_options_layout.addWidget(self.dodaj_proizvod)
        self.proizvod_options_layout.addWidget(self.ukloni_proizvod)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.on_accept)
        #self.button_box.rejected.connect(self.on_reject)

        self.dodaj_proizvod.clicked.connect(self._on_dodaj_proizvod)
        self.ukloni_proizvod.clicked.connect(self._on_ukloni_proizvod)

        #self._populate_table()

        self.plugin_proizvodi_layout.addLayout(self.proizvod_options_layout)
        self.plugin_proizvodi_layout.addWidget(self.table_view)
        self.plugin_proizvodi_layout.addWidget(self.button_box)

        self.setLayout(self.plugin_proizvodi_layout)

    def on_accept(self):

        return self.accept()

    def _prikaz_svih_proizvoda_iz_baze(self):

        self.set_model(SviProizvodiListModel())
        return

    def set_model(self, model):

        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def _on_dodaj_proizvod(self):
        dialog = DodajProizvodDialog(self.parent())
        # znaci da je neko odabrao potvrdni odgovor na dijalog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            #unos podataka u bazu sto je korisnik uneo
            tmpL = dialog.get_data()
            self._c.execute("INSERT INTO proizvodi (naziv_proizvoda, rok_upotrebe, temp_cuvanja) VALUES (:nazivP , :rokU, :temp)" ,{'nazivP' : tmpL['nazivP'], 'rokU' : tmpL['rokUpotrebe'], 'temp' : tmpL['temp']} )
            #self.hala_naziv = list(result.fetchall())
            #self.hala_naziv = self.hala_naziv[0]
           # self._conn.commit()

            #GET LAST INSERTED ID
            lastID = self._c.lastrowid # zadnji uneti id
            uneti_podaci = dialog.get_data()
            uneti_podaci['productID'] = lastID

            #self._prikaz_svih_proizvoda_iz_baze()
            self.table_view.model().add(uneti_podaci)
            self._conn.commit()

    def _on_ukloni_proizvod(self):
        rows = sorted(set(index.row() for index in
                      self.table_view.selectedIndexes())) #dobijamo redni br reda koji je izabrao korisnik
        if len(rows) == 0:
            return
        selected_proizvodID = self.table_view.model().get_id_kliknutog_proizvoda(rows[0])

        res = self._c.execute("SELECT proizvodi_id FROM proizvodi_hale WHERE proizvodi_id = :pID" , {'pID' : selected_proizvodID})
        res = self._c.fetchone()
        if res != None:
            QtWidgets.QMessageBox.warning(self,
            "Proizvod postoji u hali", "Proizvod postoji u hali!", QtWidgets.QMessageBox.Ok)
            return False

        self.table_view.model().remove(self.table_view.selectedIndexes())
    def get_data(self):
        return{}
