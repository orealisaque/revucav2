from django.forms import ClearableFileInput

class ImagePreviewFileInput(ClearableFileInput):
    template_name = 'ads/widgets/custom_file_input.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'attrs': {
                'class': 'hidden',
                'accept': 'image/*',
                'multiple': True,
                'data-preview': f'preview-{name}',
                **context['widget']['attrs']
            }
        })
        return context

class VideoPreviewFileInput(ClearableFileInput):
    template_name = 'ads/widgets/video_file_input.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'attrs': {
                'class': 'hidden',
                'accept': 'video/*',
                'data-preview': f'preview-{name}',
                **context['widget']['attrs']
            }
        })
        return context 