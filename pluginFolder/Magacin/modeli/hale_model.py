from PySide2 import QtCore
import os
import sqlite3
from ..sqlite_init import konekcija_ka_bazi
####################################################
#def konekcija_ka_bazi():
#    return sqlite3.connect('magacin.db')
####################################################

class HaleListModel(QtCore.QAbstractTableModel):

         # Koristi se tabelarni model,jer cemo podatke posmatrati kao tabelu, i u tabeli ih prikazivati.
        # Svaki tabelarni model ima redove i kolone.

    def __init__(self):
        super().__init__()
        # Inicijalizator modela za hale.
        # matrica, redovi su liste, a unutar tih listi se nalaze pojedinacni podaci 
        self._conn = konekcija_ka_bazi()
        self._c = self._conn.cursor()
        self._data = []
        self.ucitaj_podatke_iz_baze()

    def rowCount(self, index):
        #Vraca broj redova u modelu.
        #Parametar index - putanja do datoteke u kojoj su smesteni podaci.
        #return - vraca broj redova modela.
        return len(self._data)

    def columnCount(self, index):
        #Vraca podatak smesten na datom indeksu.
        #Parametar index - index elementa modela
        #Vracamo fiksan broj
        return 5 

    def data(self, index, role):
        # Vraca podatak smesten na datom indeksu sa datom ulogom.
        # Parametar index - index elementa modela
        # type index: QModelIndex
        # Parametar role: putanja do datoteke u kojoj su smesteni podaci.
        # Type Role: Qt.Core.Qt.XXXRole (gde je xxx konkretna uloga)
        # return vraca podatak koji se nalazi na zadatom indeksu sa zadatom ulogom
        element = self.get_element(index)
        if element is None:
            return None

        if role == QtCore.Qt.DisplayRole:
            return element

    def headerData(self, section, orientation, role):
        # Vraca podatak koji ce popuniti sekciju zaglavlja tabele.
        # Parametar section: sekcija koja je u zavisnosti od orijentacije predstavlja redni broj kolone ili reda
        # type section : int
        # Parametar orientation : odredjuje polozaj zaglavlja.
        # Type orientation : QtCore.Qt.Vertical ili Qt.Core.Qt.Horizontal
        # Parametar role: putanja do datoteke u kojoj su smesteni podaci
        # returns string - naziv sekcije zaglavlja
        if orientation != QtCore.Qt.Vertical:
            if (section == 0) and (role == QtCore.Qt.DisplayRole):
                return "id"
            elif (section == 1) and (role == QtCore.Qt.DisplayRole):
                return "naziv hale"
            elif (section == 2) and (role == QtCore.Qt.DisplayRole):
                return "tip hale"
            elif (section == 3) and (role == QtCore.Qt.DisplayRole):
                return "ukupan broj mesta"
            elif (section == 4) and (role == QtCore.Qt.DisplayRole):
                return "broj zauzetih mesta"

    def setData(self, index, value, role):
        # Postavlja vrednost na zadatom indeksu
        # Metoda je vazna ako zelimo da se nas model moze menjati.
        # Parametar index : index elementa modela
        # Type index : QModelIndex
        # Parametar value : nvoa vrednost koju zelimo da postavimo
        # Type value: str - vrednost koja ce biti dodeljena
        # Parametar role: putanja do datoteke u kojoj su smesteni podaci.
        # returns bool podatak o uspesnosti izmene.
        try:
            if value == "":
                return False
            self._data[index.row()][index.column()] = value
            self.dataChanged()
            return True
        except:
            return False

    def flags(self, index):
        # Vraca flagove koji su aktivni za dati indeks modela.
        # return object - flagovi koji treba da budu aktivirani
        # ne damo da menja datum rodjenja (primera radi)
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        # sve ostale podatke korisnik moze da menja

    def get_element(self, index : QtCore.QModelIndex):
        # Dobavlja podatak smesten na zadatom indeksu,ako je indeks validan.
        # Pomocna metoda nase klase
        # return: object - vrednost na indeksu
        if index.isValid():
            element = self._data[index.row()][index.column()]
            if element:
                return element
        return None

    def remove(self, indices):
        # Uklanja elemente iz modela na zadatim indeksima. Mozemo uklanjati vise redova u jednom pozivu metode.
        # Parametar indices : indeks elementa modela
        # Type indices : list - Lista QModelIndex-a
        # za na osnovu indeksa, dobijamo njihove redove, posto za jedan red je vezano pet indeksa (za kolone)
        # pravimo skup koji ce dati samo jedinstvene brojeve redova
        # uklanjanje vrsimo od nazad, jer ne zelimo da nam brojevi redova nakon uklanjanja odu van opsega.
        indices = sorted(set(map(lambda x: x.row(), indices)), reverse=True)
        for i in indices:
            #### obrisi iz baze
            temp_id = self.get_id_kliknute_hale(i)
            result = self._conn.execute("""DELETE FROM rashladne_hale WHERE rashladne_hale_id = :ID""" , {'ID' : temp_id} )
            self._conn.commit()
            result = self._conn.execute("""DELETE FROM proizvodi_hale WHERE rashladne_hale_id = :ID""" , {'ID' : temp_id} )
            self._conn.commit()
            ##################
            self.beginRemoveRows(QtCore.QModelIndex(), i, i)
            del self._data[i]
            self.endRemoveRows()

    def add(self, data : dict):
        # Dodaj u bazu
        self.beginInsertRows(QtCore.QModelIndex(), len(self._data), len(self._data))
        ######
        result = self._conn.execute(""" SELECT naziv_hale FROM tip_hale where tip_hale_id=:idHere;""", {'idHere':data['tipHaleID'] })
        resultTipNaziv = list(result.fetchall())
        self._conn.commit()
        self._data.append([data['haleID'], data['nazivHale'], resultTipNaziv[0][0], data['brMesta'], data['brZazuzetihMesta']])
        self.endInsertRows()

    def ucitaj_podatke_iz_baze(self):
        result = self._conn.execute(""" SELECT rashladne_hale_id, ime_hale, naziv_hale, ukupan_br_mesta, br_zauzetih_mesta
FROM rashladne_hale INNER JOIN tip_hale ON rashladne_hale.tip_hale_id = tip_hale.tip_hale_id;
        """)
        self._data = list(result.fetchall())
        self._conn.commit()
#todo delete
    def get_id_kliknute_hale(self, index):
        return self._data[index][0]
