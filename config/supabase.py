from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
print("SUPABASE_URL>>>>", SUPABASE_URL)
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print("SUPABASE_KEY>>>>", SUPABASE_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)