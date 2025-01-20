def user_progress(request):
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    fields = {
        'Nome completo': bool(user.get_full_name()),
        'Foto do perfil': bool(user.foto_perfil),
        'WhatsApp': bool(user.phone),
        'Biografia': bool(user.bio),
        'Estado': bool(user.estado),
        'Cidade': bool(user.cidade),
    }
    
    missing_fields = [field for field, value in fields.items() if not value]
    
    return {
        'profile_status': {
            'missing_fields': missing_fields,
            'complete': len(missing_fields) == 0,
        }
    } 