from django.contrib.auth.models import User, Group
from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        # Remove commas and convert to Decimal
        val1 = Decimal(str(value).replace(',', ''))
        val2 = Decimal(str(arg).replace(',', ''))
        
        result = val1 - val2
        return result
        
    except Exception as e:
        print(f"ERROR in subtract filter: {e}")
        print(f"ERROR: value = {repr(value)}, arg = {repr(arg)}")
        return 0
