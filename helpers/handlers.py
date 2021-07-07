import csv

from django.http import HttpResponse


class ExportCsvMixin:
    def export_items_to_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields if field.name != 'password']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        [writer.writerow([getattr(obj, field) for field in field_names]) for obj in queryset]                           
        return response

