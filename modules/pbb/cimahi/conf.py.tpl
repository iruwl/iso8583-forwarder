db_url = 'oracle://pospbb:FIXME@10.3.1.55:1521/simpbb'

db_schema = 'pbb'
#db_schema = None # Saat devel

# Tuning
# http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html
db_pool_size = 50
db_max_overflow = 100

# Denda bila lewat jatuh tempo
persen_denda = 2.0

nip_rekam_byr_sppt = '999999999'

# Apakah perlu update tabel sppt ? Karena bisa jadi sudah dilakukan oleh
# trigger di tabel pembayaran_sppt.
is_update_sppt = True

host = {
    'bjb_with_suffix': {
        'kd_kanwil': '01',
        'kd_kantor': '01',
        'kd_tp': '04',
        },
    'btn': {
        'kd_kanwil': '01',
        'kd_kantor': '11',
        'kd_tp': '44',
        },
    'pos': {
        'kd_kanwil': '01',
        'kd_kantor': '01',
        'kd_tp': '99',
        },
    'bsm': {
        'kd_kanwil': '01',
        'kd_kantor': '01',
        'kd_tp': '54',
        },
    }
