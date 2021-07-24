from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import Group

class GroupFilter(SimpleListFilter):
    title = 'user groups'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        # print(request.GET)
        groups = Group.objects.all()
        return (
            (group.id, group.name) for group in groups
        ) 

    def queryset(self, request, queryset):
        if self.value() == 'all' or self.value() is None:
            return queryset
        else:
            group = Group.objects.get(id=self.value())
            return queryset.filter(groups__name__in=[group])