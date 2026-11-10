from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdoptionApplicationForm, WalkingBookingForm
from .models import AdoptionApplication, AdoptionContract, Pet, WalkingBooking


def index(request):
  filters = {f: request.GET[f] for f in ('species', 'status', 'gender') if request.GET.get(f)}
  pets = Pet.objects.filter(**filters).order_by('-admission_date')
  q = request.GET.get('q')
  if q:
    pets = pets.filter(Q(name__icontains=q) | Q(breed__icontains=q))
  query = request.GET.copy()
  query.pop('page', None)
  return render(request, 'index.html', {
      'page_obj': Paginator(pets, 20).get_page(request.GET.get('page')),
      'query': query.urlencode(),
      'statuses': Pet.STATUS_CHOICES,
      'genders': Pet.GENDER_CHOICES,
  })


def pet_detail(request, pk):
  pet = get_object_or_404(Pet, pk=pk)
  blocked = pet.status in ('quarantine', 'treatment')
  form, walking_form = AdoptionApplicationForm(), WalkingBookingForm()
  error = success = None

  if request.method == 'POST':
    if not request.user.is_authenticated:
      return redirect('login')
    if blocked:
      error = 'Этот питомец находится на карантине или лечении. Взаимодействие с ним временно заблокировано.'
    elif 'adopt_submit' in request.POST:
      form = AdoptionApplicationForm(request.POST)
      if form.is_valid():
        form.instance.user, form.instance.pet = request.user, pet
        form.save()
        form, success = AdoptionApplicationForm(), 'Ваша анкета на усыновление успешно отправлена!'
    elif 'walk_submit' in request.POST:
      walking_form = WalkingBookingForm(request.POST)
      if walking_form.is_valid():
        walking_form.instance.volunteer, walking_form.instance.pet = request.user, pet
        walking_form.save()
        walking_form, success = WalkingBookingForm(), 'Вы успешно записались на прогулку с питомцем!'

  return render(request, 'pet_detail.html', {
      'pet': pet, 'form': form, 'walking_form': walking_form,
      'blocked': blocked, 'error': error, 'success': success,
  })


@login_required
def profile_view(request):
  return render(request, 'profile.html', {
      'applications': AdoptionApplication.objects.filter(user=request.user),
      'bookings': WalkingBooking.objects.filter(volunteer=request.user),
  })


def register_view(request):
  form = UserCreationForm(request.POST or None)
  if form.is_valid():
    login(request, form.save())
    return redirect('index')
  return render(request, 'register.html', {'form': form})


@login_required
@transaction.atomic
def sign_contract(request, application_id):
  application = get_object_or_404(AdoptionApplication, pk=application_id)
  pet = application.pet
  AdoptionContract.objects.create(application=application)
  application.status = 'completed'
  application.save()
  pet.status = 'adopted'
  pet.save()
  AdoptionApplication.objects.filter(pet=pet).exclude(pk=application.id).update(status='rejected')
  return redirect('pet_detail', pk=pet.id)


@login_required
def download_contract_txt(request, application_id):
  application = get_object_or_404(AdoptionApplication, pk=application_id, user=request.user)
  pet = application.pet
  text = f"""МУНИЦИПАЛЬНЫЙ ПРИЮТ ДЛЯ ЖИВОТНЫХ «ЛАПА ПОМОЩИ»
ДОГОВОР ОБ УСЫНОВЛЕНИИ ПИТОМЦА № {application.id}

Дата составления: {application.created_at:%d.%m.%Y %H:%M}

1. СТОРОНЫ ДОГОВОРА
Приют «Лапа помощи» в лице администратора и Гражданин(ка): {request.user.username},
именуемый(-ая) в дальнейшем «Усыновитель».

2. ДАННЫЕ О ЖИВОТНОМ
- Кличка: {pet.name}
- Вид: {pet.species}
- Порода: {pet.breed or 'Не указана'}
- Пол: {pet.get_gender_display()}
- Возраст: {pet.age}

3. УСЛОВИЯ И ИНФОРМАЦИЯ ОТ УСЫНОВИТЕЛЯ
Жилищные условия:
{application.housing_conditions}

Опыт содержания животных:
{application.experience}

4. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ
Усыновитель обязуется обеспечить надлежащий уход, содержание и ветеринарное обслуживание животного.
Статус заявки: {application.get_status_display()}

М.П. (Подпись / Дата)
Усыновитель: ___________________________ / {request.user.username}
"""
  response = HttpResponse(text, content_type='text/plain; charset=utf-8')
  response['Content-Disposition'] = f'attachment; filename="Adoption_Contract_{application.id}.txt"'
  return response
