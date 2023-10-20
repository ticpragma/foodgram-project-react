from django.contrib import admin
from .models import Tag, Ingredient, Recipe, Favorite

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Favorite)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass
