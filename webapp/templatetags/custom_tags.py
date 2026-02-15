from django import template

register = template.Library()


@register.simple_tag
def remove_from_session(request, key):
  """Attempts to remove a key from the request.session object.

  **Note:** Modifying session data directly in templates is not recommended.
  """
  if key in request.session:
    del request.session[key]
    request.session.save()  # Manually save the modified session
  return ""


@register.filter
def in_groups(user, group_list):
    group_names = [g.strip() for g in group_list.split(',')]
    return user.groups.filter(name__in=group_names).exists() or user.is_superuser