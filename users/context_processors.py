def user_progress(request):
    if not request.user.is_authenticated:
        return {
            'profile_progress': [],
            'total_progress': 0,
            'can_publish': False
        }
    
    user = request.user
    progress_items = [
        {
            'label': 'Foto do Perfil',
            'complete': bool(user.foto),
            'url': 'users:profile_edit',
            'icon': 'fa-camera',
            'required': True,
            'message': 'Adicione uma foto para aumentar sua credibilidade'
        },
        {
            'label': 'WhatsApp',
            'complete': bool(user.whatsapp),
            'url': 'users:profile_edit',
            'icon': 'fa-phone',
            'required': True,
            'message': 'Número para contato é obrigatório'
        },
        {
            'label': 'Cidade',
            'complete': bool(user.cidade_ref),
            'url': 'users:profile_edit',
            'icon': 'fa-map-marker-alt',
            'required': True,
            'message': 'Informe sua cidade para anunciar'
        },
        {
            'label': 'Descrição',
            'complete': bool(user.bio),
            'url': 'users:profile_edit',
            'icon': 'fa-user-edit',
            'required': False,
            'message': 'Uma boa descrição aumenta suas chances'
        },
        {
            'label': 'Instagram',
            'complete': bool(user.instagram),
            'url': 'users:profile_edit',
            'icon': 'fa-instagram',
            'required': False,
            'message': 'Conecte suas redes sociais'
        }
    ]
    
    required_items = [item for item in progress_items if item['required']]
    completed_required = len([item for item in required_items if item['complete']])
    can_publish = completed_required == len(required_items)
    
    completed = len([item for item in progress_items if item['complete']])
    total_progress = int((completed / len(progress_items)) * 100)
    
    return {
        'profile_progress': progress_items,
        'total_progress': total_progress,
        'profile_complete': total_progress == 100,
        'can_publish': can_publish,
        'missing_required': len(required_items) - completed_required
    } 