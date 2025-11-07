import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the social media campaigns migration."""
    
    # Get database connection string
    db_uri = os.getenv("SUPABASE_URI")
    if not db_uri:
        print("Error: SUPABASE_URI environment variable not set")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_uri)
        cursor = conn.cursor()
        
        # Read migration file
        with open("migration-social-media-campaigns.sql", "r") as f:
            migration_sql = f.read()
        
        # Execute migration
        print("Running social media campaigns migration...")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('social_media_campaigns', 'social_media_posts', 'campaign_audience')
        """)
        
        tables = cursor.fetchall()
        print(f"✅ Created tables: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_migration()
