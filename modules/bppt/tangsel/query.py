from sqlalchemy import func
from tools import (
    round_up,
    DbTransactionID,
    )

from conf import persen_denda
from db_tools import hitung_denda

class BaseQuery(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession

class OtherQuery(BaseQuery):
    def query_invoice(self, invoice_id_raw):
        Inv = self.models.Invoice
        Izin = self.models.Perizinan
        Pemohon = self.models.Pemohon
        Permohonan = self.models.Permohonan
        return self.DBSession.query(Inv.id, Inv.kd_bayar, Inv.jumlah,
                  Inv.date_skrd, Inv.date_expire, Inv.nominal, Inv.denda,
                  Inv.jum_bayar, Inv.ref_bayar, Inv.is_bayar, Inv.date_bayar,
                  Inv.tmpermohonan_id, Izin.n_perizinan,
                  Pemohon.n_pemohon.label('nama_wp'),
                  Permohonan.alamatizin.label('lokasi_izin')
                  ).\
            join(Izin).join(Permohonan).join(Pemohon).\
            filter(Inv.kd_bayar==invoice_id_raw)

    def get_payment(self, invoice):
        q = self.query_payment(invoice)
        return q.first()

    def query_payment(self, invoice):
        q = self.DBSession.query(self.models.Invoice)
        return self.filter_payment(q, invoice)
 
    def filter_payment(self, q, invoice):
         return q.filter_by(id=invoice.id)

class NTP(DbTransactionID):
    # Override
    def is_found(self, trx_id):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(ntp=trx_id)
        return q.first()


class Invoice(OtherQuery):
    def __init__(self, models, DBSession, invoice_id_raw):
        OtherQuery.__init__(self, models, DBSession)
        self.invoice_id_raw = invoice_id_raw
        q = self.query_invoice(invoice_id_raw)
        self.invoice = q.first()


class CalculateInvoice(Invoice):
    def __init__(self, *args, **kwargs):
        Invoice.__init__(self, *args, **kwargs)
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()
            print self.paid
            
    def hitung(self):
        self.tagihan = self.invoice.jumlah and round_up(self.invoice.jumlah) or 0
        bulan, denda = hitung_denda(self.tagihan, self.invoice.date_expire, persen_denda)
        self.denda = denda
        self.bulan = bulan
        self.total = int(self.tagihan) + int(self.denda)

    def is_paid(self):
        if self.invoice.is_bayar:
            return True
        
        #TODO apa harus dihitung juga denda dan jum_bayar
        nominal = self.invoice.nominal  and round_up(self.invoice.nominal) or 0
        return nominal >= self.tagihan


FIELD_ARSIP = ('no_ssrd', 'date_ssrd', 'no_sts', 'date_sts', 'jumlah_bayar',
    'cara_bayar', 'ref_baar', 'date_bayar')


class Reversal(CalculateInvoice):
    def __init__(self, *args, **kwargs):
        for arg in args:
            print arg
        CalculateInvoice.__init__(self, *args, **kwargs)
        self.payment = self.get_payment()

    # Override
    def get_payment(self):
        if self.invoice:
            return CalculateInvoice.get_payment(self, self.invoice)

    def set_unpaid(self, arsip=None):
        # if arsip:
            # self.arsip(arsip)
        pay = self.query_payment(self.invoice).first()
        pay.date_bayar = None
        pay.cara_bayar = None
        pay.ref_bayar = None
        pay.nominal = None
        pay.denda = None
        pay.jum_bayar = None
        pay.denda_masaberlaku = None
        pay.is_bayar = 0
        self.DBSession.add(pay)
        self.DBSession.flush()

    # def arsip(self, row):
        # source = self.payment.to_dict()
        # target = dict()
        # for field in FIELD_ARSIP:
            # if field in source:
                # target[field] = source[field]
        # row.from_dict(target)

class Query(BaseQuery):
    def get_izin_by_name(self, nama):
        q = self.DBSession.query(self.models.Izin).filter_by(nama=nama)
        return q.first()

    def get_iso_payment(self, pay):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(
                id_pendaftaran=str(pay.id)).order_by(
                self.models.IsoPayment.id.desc())
        return q.first()