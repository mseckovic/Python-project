from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt
from ...modeli.proizvodi_iz_hale_model import ProizvodiIzHaleListModel
from .dodaj_proizvod_u_halu import DodajProizvodUHaluDialog
from .ukloni_proizvod_iz_hale import UkloniProizvodIzHaleDialog
from ...sqlite_init import konekcija_ka_bazi

class AddPregledProizvodaIzHaleDialog(QtWidgets.QDialog):

    def __init__(self, parent=None, halaID=None):
        super().__init__(parent)
        self.this_halaID = halaID
        self._conn = konekcija_ka_bazi()
        self._c = self._conn.cursor()
        result = self._conn.execute("SELECT ime_hale FROM rashladne_hale WHERE rashladne_hale_id =:halaid" ,{'halaid' : self.this_halaID} )
        self.hala_naziv = list(result.fetchall())
        self.hala_naziv = self.hala_naziv[0]
        self._conn.commit()



        self.setWindowTitle("Pregled Proizvoda iz [ " + self.hala_naziv[0]+ " ]")
        self.resize(700, 550)

        self.proizvod_options_layout = QtWidgets.QHBoxLayout()

        self.dodaj_proizvod = QtWidgets.QPushButton(QIcon("resources/icons/plus.png"), "Dodaj Proizvod")
        self.ukloni_proizvod = QtWidgets.QPushButton(QIcon("resources/icons/minus.png"), "Ukloni proizvod")
        self.plugin_proizvodi_layout = QtWidgets.QVBoxLayout()

        self.table_view = QtWidgets.QTableView(self)
        self._prikaz_proizvoda_iz_hale_baza()
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.proizvod_options_layout.addWidget(self.dodaj_proizvod)
        self.proizvod_options_layout.addWidget(self.ukloni_proizvod)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.on_accept)

        self.plugin_proizvodi_layout.addLayout(self.proizvod_options_layout)
        self.plugin_proizvodi_layout.addWidget(self.table_view)
        self.plugin_proizvodi_layout.addWidget(self.button_box)

        self.dodaj_proizvod.clicked.connect(self._on_dodaj_proizvod_dialog)
        self.ukloni_proizvod.clicked.connect(self._on_ukloni_proizvod)

        self.setLayout(self.plugin_proizvodi_layout)

    def on_accept(self):

        return self.accept()

    def _prikaz_proizvoda_iz_hale_baza(self):

        self.set_model(ProizvodiIzHaleListModel(self.this_halaID))
        return

    def set_model(self, model):

        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def _on_dodaj_proizvod_dialog(self):
        dialog = DodajProizvodUHaluDialog(self.parent() , self.hala_naziv[0], self.this_halaID )
        # znaci da je neko odabrao potvrdni odgovor na dijalog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            #self.table_view.model().add(dialog.get_data())
            tmpL = dialog.get_data()
            #provera da li uneti podatak postoji, ako postoji samo povecaj kolicinu
            self._c.execute("SELECT proizvodi_hale_id FROM proizvodi_hale WHERE rashladne_hale_id = :rhID AND proizvodi_id = :pID" , {'rhID' : tmpL['halaID'], 'pID' : tmpL['proizvodID']})
            row1 = self._c.fetchone()
            self._conn.commit()
            if (row1 == None):
                self._c.execute("INSERT INTO proizvodi_hale (proizvodi_id, rashladne_hale_id, kolicina_u_hali) VALUES (:pID , :rhID, :kolicina)" ,{'pID' : tmpL['proizvodID'], 'rhID' : tmpL['halaID'], 'kolicina' : tmpL['kolicina']} )
                self._conn.commit()
            else:
                self._c.execute("""
                UPDATE proizvodi_hale SET kolicina_u_hali = (
                SELECT kolicina_u_hali FROM proizvodi_hale WHERE rashladne_hale_id = :rhID AND proizvodi_id = :pID
                ) + :kolicina WHERE rashladne_hale_id = :rhID AND proizvodi_id = :pID
                 """,{'pID' : tmpL['proizvodID'], 'rhID' : tmpL['halaID'] , 'kolicina' : tmpL['kolicina'] } )
                self._conn.commit()

            """
            #GET LAST INSERTED ID
            lastID = self._c.lastrowid # zadnji uneti id
            uneti_podaci = dialog.get_data()
            uneti_podaci['proizvodiHaleID'] = lastID
            """

            #self._prikaz_svih_proizvoda_iz_baze()
            #self.table_view.model().add(uneti_podaci)
            #update rashladne hale
            self._c.execute("UPDATE rashladne_hale SET br_zauzetih_mesta = :brZauzetih WHERE rashladne_hale_id = :rhID;",{'brZauzetih' : tmpL['novBrZauzetih'], 'rhID' : tmpL['halaID']} )
            self._conn.commit()
            self._prikaz_proizvoda_iz_hale_baza()

    def _on_ukloni_proizvod(self):
        rows = sorted(set(index.row() for index in
                      self.table_view.selectedIndexes())) #dobijamo redni br reda koji je izabrao korisnik
        if len(rows) == 0:
            return
        selected_pID = self.table_view.model().get_id_kliknuti_proizvod(rows[0])
        selected_naziv = self.table_view.model().get_naziv_kliknuti_proizvod(rows[0])
        selected_kolicina = self.table_view.model().get_kolicina_kliknuti_proizvod(rows[0])
        dialog = UkloniProizvodIzHaleDialog(self.parent() , self.this_halaID , selected_naziv , selected_pID, selected_kolicina )
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.get_data()
            self._prikaz_proizvoda_iz_hale_baza()
        return
    def get_data(self):
        return {}
