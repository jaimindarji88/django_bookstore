from django import template

register = template.Library()

@register.filter()
def to_cents(val):
    return int(val * 100)

@register.filter()
def pluralize(val):
    ret_val = ''
    if val > 1:
        ret_val = 's'
    return ret_val