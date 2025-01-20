from django.db import connection

def fix_migrations():
    with connection.cursor() as cursor:
        # Remove todas as migrações existentes
        cursor.execute("DELETE FROM django_migrations;")
        
        # Insere as migrações na ordem correta
        migrations = [
            ('contenttypes', '0001_initial'),
            ('contenttypes', '0002_remove_content_type_name'),
            ('auth', '0001_initial'),
            ('auth', '0002_alter_permission_name_max_length'),
            ('auth', '0003_alter_user_email_max_length'),
            ('auth', '0004_alter_user_username_opts'),
            ('auth', '0005_alter_user_last_login_null'),
            ('auth', '0006_require_contenttypes_0002'),
            ('auth', '0007_alter_validators_add_error_messages'),
            ('auth', '0008_alter_user_username_max_length'),
            ('auth', '0009_alter_user_last_name_max_length'),
            ('auth', '0010_alter_group_name_max_length'),
            ('auth', '0011_update_proxy_permissions'),
            ('auth', '0012_alter_user_first_name_max_length'),
            ('sites', '0001_initial'),
            ('sites', '0002_alter_domain_unique'),
            ('users', '0001_initial'),
            ('admin', '0001_initial'),
            ('admin', '0002_logentry_remove_auto_add'),
            ('admin', '0003_logentry_add_action_flag_choices'),
            ('sessions', '0001_initial'),
            ('account', '0001_initial'),
            ('account', '0002_email_max_length'),
            ('socialaccount', '0001_initial'),
            ('socialaccount', '0002_token_max_lengths'),
            ('socialaccount', '0003_extra_data_default_dict'),
        ]
        
        for app, migration in migrations:
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW());",
                [app, migration]
            )

if __name__ == '__main__':
    import django
    django.setup()
    fix_migrations() 