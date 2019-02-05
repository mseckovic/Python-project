from PySide2 import QtCore
import os
import sqlite3
from ..sqlite_init import konekcija_ka_bazi
####################################################
#def konekcija_ka_bazi():
#    return sqlite3.connect('magacin.db')
####################################################

class ProizvodiIzHaleListModel(QtCore.QAbstractTableModel):

    def __init__(self, halaID):
        super().__init__()
        self.this_halaID = halaID
        # matrica, redovi su liste, a unutar tih listi se nalaze pojedinacni podaci o korisniku iz imenika
        self._conn = konekcija_ka_bazi()
        self._c = self._conn.cursor()
        self._data = []
        self.ucitaj_podatke_iz_baze()

    def rowCount(self, index):

        return len(self._data)

    def columnCount(self, index):
        return 4 #fiksan br vracamo

    def data(self, index, role):

        element = self.get_element(index)
        if element is None:
            return None

        if role == QtCore.Qt.DisplayRole:
            return element

    def headerData(self, section, orientation, role):

        if orientation != QtCore.Qt.Vertical:
            if (section == 0) and (role == QtCore.Qt.DisplayRole):
                return "id"
            elif (section == 1) and (role == QtCore.Qt.DisplayRole):
                return "naziv proizvoda"
            elif (section == 2) and (role == QtCore.Qt.DisplayRole):
                return "datum isteka roka"
            elif (section == 3) and (role == QtCore.Qt.DisplayRole):
                return "količina proizvoda u hali"

    def setData(self, index, value, role):

        try:
            if value == "":
                return False
            self._data[index.row()][index.column()] = value
            self.dataChanged()
            return True
        except:
            return False

    def flags(self, index):

        # ne damo da menja datum rodjenja (primera radi)
        #if index.column() != 4:
        #    return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        # sve ostale podatke korisnik moze da menja
        #else:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def get_element(self, index : QtCore.QModelIndex):

        if index.isValid():
            element = self._data[index.row()][index.column()]
            if element:
                return element
        return None

    def remove(self, indices):

        # za na osnovu indeksa, dobijamo njihove redove, posto za jedan red je vezano pet indeksa (za kolone)
        # pravimo skup koji ce dati samo jedinstvene brojeve redova
        # uklanjanje vrsimo od nazad, jer ne zelimo da nam brojevi redova nakon uklanjanja odu van opsega.
        indices = sorted(set(map(lambda x: x.row(), indices)), reverse=True)
        for i in indices:
            self.beginRemoveRows(QtCore.QModelIndex(), i, i)
            del self._data[i]
            self.endRemoveRows()

    def add(self, data : dict):

        self.beginInsertRows(QtCore.QModelIndex(), len(self._data), len(self._data))
        self._data.append([data["proizvodiHaleID"], data["nazivProizvoda"], data["kolicina"]])
        self.endInsertRows()

    def ucitaj_podatke_iz_baze(self):
        result = self._conn.execute("""
        SELECT proizvodi_hale_id , naziv_proizvoda , rok_upotrebe , kolicina_u_hali, proizvodi_hale.proizvodi_id
        FROM proizvodi_hale INNER JOIN proizvodi ON
        proizvodi_hale.proizvodi_id = proizvodi.proizvodi_id
        WHERE rashladne_hale_id = :halaID
        """ ,{'halaID' : self.this_halaID})
        self._data = list(result.fetchall())
        self._conn.commit()
        self._conn.close()
#todo delete
    def get_id_kliknuti_proizvod(self, index):
        return self._data[index][4]
    def get_naziv_kliknuti_proizvod(self, index):
        return self._data[index][1]
    def get_kolicina_kliknuti_proizvod(self, index):
        return self._data[index][3]
