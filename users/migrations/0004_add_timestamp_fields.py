from django.db import migrations
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_initial_data'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                BEGIN
                    ALTER TABLE users_acompanhanteprofile 
                    ADD COLUMN created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP;
                EXCEPTION WHEN duplicate_column THEN
                    NULL;
                END;
                
                BEGIN
                    ALTER TABLE users_acompanhanteprofile 
                    ADD COLUMN updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP;
                EXCEPTION WHEN duplicate_column THEN
                    NULL;
                END;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE users_acompanhanteprofile 
            DROP COLUMN IF EXISTS created_at,
            DROP COLUMN IF EXISTS updated_at;
            """
        )
    ] 