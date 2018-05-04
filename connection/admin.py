from django.contrib import admin

from connection.models import Connection


class ConnectionAdmin(admin.ModelAdmin):
    model = Connection


admin.site.register(Connection, ConnectionAdmin)
