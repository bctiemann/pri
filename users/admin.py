from django.contrib import admin

from users.models import User, Customer, MusicGenre


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',)


class MusicGenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(MusicGenre, MusicGenreAdmin)
