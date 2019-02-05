from PySide2 import QtWidgets
from PySide2 import QtGui
from ..modeli.hale_model import HaleListModel
from .dialogs.dodaj_halu_u_magacin import DodajHaluUMagacinDialog
from .dialogs.pregled_svih_proizvoda import AddPregledSvihProizvodaDialog
from .dialogs.pregled_proizvoda_iz_hale import AddPregledProizvodaIzHaleDialog
from ..sqlite_init import konekcija_ka_bazi



class HaleListWidget(QtWidgets.QWidget):
    #Klasa koja predstavlja glavni widget za Hale.
    def __init__(self, parent=None):
        self._conn = konekcija_ka_bazi()
        self._c = self._conn.cursor()

        super().__init__(parent)
        self.vbox_layout = QtWidgets.QVBoxLayout()
        self.hbox_layout = QtWidgets.QHBoxLayout()
        self.hbox_layout2 = QtWidgets.QHBoxLayout()
        self.dodaj_halu = QtWidgets.QPushButton(QtGui.QIcon("resources/icons/plus.png"), "Dodaj halu u magacin", self)
        self.ukloni_halu = QtWidgets.QPushButton(QtGui.QIcon("resources/icons/minus.png"), "Ukloni halu iz magacina", self)
        self.pregled_svih_proizvoda = QtWidgets.QPushButton(QtGui.QIcon("resources/icons/binocular-small.png"), "Pregled svih proizvoda", self)
        self.pregled_proizvoda_iz_hale = QtWidgets.QPushButton(QtGui.QIcon("resources/icons/box.png"), "Pregled proizvoda iz hale", self)
        self.osvezi_prikaz = QtWidgets.QPushButton(QtGui.QIcon("resources/icons/arrow-circle-225-left.png"), "Osveži Prikaz", self)

        self.hbox_layout.addWidget(self.pregled_svih_proizvoda)

        self.hbox_layout2.addWidget(self.dodaj_halu)
        self.hbox_layout2.addWidget(self.ukloni_halu)
        self.hbox_layout2.addWidget(self.pregled_proizvoda_iz_hale)
        self.hbox_layout2.addWidget(self.osvezi_prikaz)

        self.table_view = QtWidgets.QTableView(self)

        self._show_hale_from_db()
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        self.dodaj_halu.clicked.connect(self._on_dodaj_halu)
        self.ukloni_halu.clicked.connect(self._on_ukloni_halu)
        self.pregled_svih_proizvoda.clicked.connect(self._on_pregled_svih_proizvoda_prikaz)
        self.pregled_proizvoda_iz_hale.clicked.connect(self._on_pregled_proizvoda_iz_hale)
        self.osvezi_prikaz.clicked.connect(self._show_hale_from_db)


        self.vbox_layout.addLayout(self.hbox_layout)
        self.vbox_layout.addLayout(self.hbox_layout2)
        self.vbox_layout.addWidget(self.table_view)

        self.setLayout(self.vbox_layout)

        self.actions_dict = {
            "add": QtWidgets.QAction(QtGui.QIcon("resources/icons/plus.png"), "Dodaj", self)
        }


    def set_model(self, model):
        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def _show_hale_from_db(self):
        self.set_model(HaleListModel())
        return

    def _on_dodaj_halu(self):
        dialog = DodajHaluUMagacinDialog(self.parent())
        # znaci da je neko odabrao potvrdni odgovor na dijalog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tmpL = dialog.get_data()

            result = self._c.execute("INSERT INTO rashladne_hale (ime_hale, tip_hale_id, ukupan_br_mesta, br_zauzetih_mesta) VALUES (:naziv , :id, :brMesta , 0)" ,{'naziv' : tmpL['nazivHale'], 'id' : tmpL['tipHaleID'], 'brMesta' : tmpL['brMesta']} )
            lastID = self._c.lastrowid # zadnji uneti id
            uneti_podaci = dialog.get_data()
            uneti_podaci['haleID'] = lastID
            uneti_podaci['brZazuzetihMesta'] = 0
            self._conn.commit()
            self.table_view.model().add(uneti_podaci)

            #self._show_hale_from_db()

    def _on_ukloni_halu(self):
        self.table_view.model().remove(self.table_view.selectedIndexes())

    def _on_pregled_svih_proizvoda_prikaz(self):
        dialog = AddPregledSvihProizvodaDialog(self.parent())

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.get_data()

    def _on_pregled_proizvoda_iz_hale(self):
        rows = sorted(set(index.row() for index in
                      self.table_view.selectedIndexes())) #dobijamo redni br reda koji je izabrao korisnik
        if len(rows) == 0:
            return
        selected_halaID = self.table_view.model().get_id_kliknute_hale(rows[0])


        dialog = AddPregledProizvodaIzHaleDialog(self.parent(), selected_halaID)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.get_data()
            self._show_hale_from_db()
