from .supabase_client import SupabaseConnection


class DatabaseService:
    def __init__(self):
        self.client = SupabaseConnection().get_client()

    def insert(self, table: str, data: dict):
        return self.client.table(table).insert(data).execute()

    def fetch_all(self, table: str):
        return self.client.table(table).select("*").execute()

    def fetch_by_id(self, table: str, record_id: str):
        return self.client.table(table).select("*").eq("id", record_id).execute()

    def fetch_by_field(self, table: str, field: str, value):
        """
        Búsqueda genérica por campo (ej: todos los participantes de una sesión).
        """
        return self.client.table(table).select("*").eq(field, value).execute()

    def count_by_field(self, table: str, field: str, value) -> int:
        """
        Cuenta filas por campo (usa count='exact' del cliente Supabase).
        """
        response = self.client.table(table).select("*", count="exact").eq(field, value).execute()
        # En la librería oficial, response.count contiene el número de filas si se usa count="exact"
        return response.count or 0

    def update(self, table: str, record_id: str, data: dict):
        return self.client.table(table).update(data).eq("id", record_id).execute()

    def delete(self, table: str, record_id: str):
        return self.client.table(table).delete().eq("id", record_id).execute()

