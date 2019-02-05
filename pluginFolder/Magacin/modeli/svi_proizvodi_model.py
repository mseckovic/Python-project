from PySide2 import QtCore
import os
import sqlite3
from ..sqlite_init import konekcija_ka_bazi
####################################################
#def konekcija_ka_bazi():
#    return sqlite3.connect('magacin.db')
####################################################

class SviProizvodiListModel(QtCore.QAbstractTableModel):

    def __init__(self):
        super().__init__()
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
                return "rok_upotrebe"
            elif (section == 3) and (role == QtCore.Qt.DisplayRole):
                return "temperatura čuvanja"

    def setData(self, index, value, role):
        value = value
        id_proizvoda = self._data[index.row()][0]
        if value == "":
            return False
        elif index.column() == 1:
            self._c.execute("UPDATE proizvodi SET naziv_proizvoda = :val  WHERE proizvodi_id = :pID", {"val": value, "pID": id_proizvoda})

        elif index.column() == 3:
            if not self.da_li_je_int(value):
                return False
            value = int(value)
            if (value > 100) or (value < -10):
                return False

            self._c.execute("UPDATE proizvodi SET temp_cuvanja = :val WHERE proizvodi_id = :pID", {"val": value, "pID": id_proizvoda})

        self._conn.commit()
        newData = list()
        elemIndex = 0
        for elem in self._data[index.row()]:
            if elemIndex == index.column():
                newData.append(value)
            else:
                newData.append(self._data[index.row()][elemIndex])
            elemIndex += 1
        self._data[index.row()] = tuple(newData)

        #self.dataChanged()
        return True
    def da_li_je_int(self, input):
        try:
            num = int(input)
        except ValueError:
            return False
        return True

    def flags(self, index):
        # ne damo da menja datum rodjenja (primera radi)
        if index.column() != 0 and index.column() != 2 :
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        # sve ostale podatke korisnik moze da menja
        else:
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

            #### obrisi iz baze
            temp_id = self.get_id_kliknutog_proizvoda(i)
            result = self._conn.execute("""DELETE FROM proizvodi WHERE proizvodi_id = :pID""" , {'pID' : temp_id} )
            self._conn.commit()
            ##################
            self.beginRemoveRows(QtCore.QModelIndex(), i, i)
            del self._data[i]
            self.endRemoveRows()

    def add(self, data : dict):
        #dodaj u bazu
        self.beginInsertRows(QtCore.QModelIndex(), len(self._data), len(self._data))
        self._data.append([data["productID"], data["nazivP"], data["rokUpotrebe"], data["temp"]])
        self.endInsertRows()

    def ucitaj_podatke_iz_baze(self):
        result = self._conn.execute(""" SELECT proizvodi_id, naziv_proizvoda, rok_upotrebe, temp_cuvanja FROM proizvodi;""")
        self._data = list(result.fetchall())
        self._conn.commit()
#todo delete
    def get_id_kliknutog_proizvoda(self, index):
        return self._data[index][0]
