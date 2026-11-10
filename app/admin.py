from django.contrib import admin

from .models import *


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
  list_display = ('name', 'species', 'breed', 'age', 'status', 'volier', 'admission_date')
  list_filter = ('species', 'status', 'gender', 'admission_date')
  search_fields = ('name', 'breed')
  list_editable = ('status', 'volier')


@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'pet', 'status', 'created_at')
  list_filter = ('status', 'created_at')
  list_editable = ('status',)


admin.site.register([
    Volier, VetCard, Interview, WalkingBooking,
    AdoptionContract, SponsorshipPayment, HomePhotoReport,
])
