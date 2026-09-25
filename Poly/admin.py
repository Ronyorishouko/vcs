from django.contrib import admin
from .models import do_reg, ksuit, manufacturer, terminal_model, physical_address, type_cabinet, registry, maintable
from .models import group_networker,service_wg, subnet_mask, table_files,suid_users, catalog_do_file, suid_catalog
from .models import registry_logs, logs

admin.site.register(do_reg)
admin.site.register(ksuit)
admin.site.register(manufacturer)
admin.site.register(terminal_model)
admin.site.register(physical_address)
admin.site.register(type_cabinet)
admin.site.register(registry)
admin.site.register(maintable)
admin.site.register(group_networker)
admin.site.register(service_wg)
admin.site.register(subnet_mask)
admin.site.register(table_files)
admin.site.register(suid_users)
admin.site.register(catalog_do_file)
admin.site.register(suid_catalog)
admin.site.register(registry_logs)
admin.site.register(logs)
