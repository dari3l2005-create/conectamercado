"""
Conexión OPCIONAL a MongoDB (galería de fotos del local).
En producción (Render) no hay MongoDB: si no conecta, las colecciones
quedan vacías y la galería no se usa, sin romper la app.
"""
import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB  = os.environ.get('MONGO_DB', 'mercado_media')


class _DummyCollection:
    def find(self, *a, **k):            return []
    def find_one(self, *a, **k):        return None
    def insert_one(self, *a, **k):      return None
    def delete_one(self, *a, **k):      return None
    def delete_many(self, *a, **k):     return None
    def count_documents(self, *a, **k): return 0


try:
    from pymongo import MongoClient
    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
    _client.admin.command('ping')          # verifica conexión rápido
    _db = _client[MONGO_DB]
    fotos_puestos   = _db['fotos_puestos']
    fotos_locatario = _db['fotos_locatario']
except Exception:
    fotos_puestos   = _DummyCollection()
    fotos_locatario = _DummyCollection()