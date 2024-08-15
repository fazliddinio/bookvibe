"""
Custom template filters for Uzbek language support
"""
from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.filter(name='timesince_uz')
def timesince_uzbek(value):
    """
    Convert Django's timesince output to Uzbek
    
    Examples:
    - "5 minutes" -> "5 daqiqa"
    - "1 hour" -> "1 soat"
    - "2 days" -> "2 kun"
    """
    if not value:
        return ""
    
    # Get the timesince output
    time_str = str(timesince(value))
    
    # First fix any Uzbek abbreviations that might have been auto-translated by Django
    # This handles cases where Django might output abbreviated forms
    result = time_str
    result = result.replace('dqiq', 'daqiqa')  # Fix Uzbek abbreviation
    result = result.replace('daqiqalar', 'daqiqa')  # Plural form
    result = result.replace('soatlar', 'soat')  # Plural form
    result = result.replace('kunlar', 'kun')  # Plural form
    
    # Translation dictionary - ordered by specificity (most specific first)
    translations = [
        # Plural forms first (to catch "minutes" before "minute")
        ('minutes', 'daqiqa'),
        ('minute', 'daqiqa'),
        ('hours', 'soat'),
        ('hour', 'soat'),
        ('days', 'kun'),
        ('day', 'kun'),
        ('weeks', 'hafta'),
        ('week', 'hafta'),
        ('months', 'oy'),
        ('month', 'oy'),
        ('years', 'yil'),
        ('year', 'yil'),
        ('seconds', 'soniya'),
        ('second', 'soniya'),
        # Abbreviated forms
        ('mins', 'daqiqa'),
        ('min', 'daqiqa'),
        ('hrs', 'soat'),
        ('hr', 'soat'),
        ('secs', 'soniya'),
        ('sec', 'soniya'),
        # Other common patterns
        ('minut', 'daqiqa'),
        ('minuta', 'daqiqa'),
        # Conjunctions
        (' and ', ' va '),
        ('an ', ''),
        ('a ', ''),
    ]
    
    # Apply translations
    for eng, uzb in translations:
        result = result.replace(eng, uzb)
    
    # Clean up extra spaces
    result = ' '.join(result.split())
    
    return result

