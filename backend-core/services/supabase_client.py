from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseConnection:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Supabase credentials not found. Check SUPABASE_URL and SUPABASE_KEY.")

        self.client: Client = create_client(self.url, self.key)

    def get_client(self) -> Client:
        return self.client
