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

    def update(self, table: str, record_id: str, data: dict):
        return self.client.table(table).update(data).eq("id", record_id).execute()

    def delete(self, table: str, record_id: str):
        return self.client.table(table).delete().eq("id", record_id).execute()
