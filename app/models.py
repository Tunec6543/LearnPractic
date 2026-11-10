from django.contrib.auth.models import User
from django.db import models


class Volier(models.Model):
  number = models.CharField('Номер/название вольера', max_length=50, unique=True)
  sector = models.CharField('Сектор приюта', max_length=100)
  capacity = models.PositiveIntegerField('Вместимость', default=1)

  def __str__(self):
    return f'Вольер №{self.number} ({self.sector})'

  class Meta:
    verbose_name = 'Вольер'
    verbose_name_plural = 'Вольеры'


class Pet(models.Model):
  STATUS_CHOICES = [
      ('available', 'Доступен'),
      ('quarantine', 'На карантине'),
      ('treatment', 'На лечении'),
      ('adopted', 'Обрёл дом'),
  ]
  GENDER_CHOICES = [('male', 'Мальчик'), ('female', 'Девочка')]

  name = models.CharField('Кличка', max_length=100)
  species = models.CharField('Вид (собака/кошка)', max_length=50)
  breed = models.CharField('Порода', max_length=100, blank=True, null=True)
  age = models.PositiveIntegerField('Возраст (лет/месяцев)')
  gender = models.CharField('Пол', max_length=10, choices=GENDER_CHOICES)
  status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='available')
  description = models.TextField('История и характер', blank=True, null=True)
  photo = models.ImageField('Фотография', upload_to='pets/', blank=True, null=True)
  volier = models.ForeignKey(
      Volier, on_delete=models.SET_NULL, null=True, blank=True,
      related_name='pets', verbose_name='Вольер',
  )
  admission_date = models.DateField('Дата поступления', auto_now_add=True)

  def __str__(self):
    return f'{self.name} ({self.species}, {self.get_status_display()})'

  class Meta:
    verbose_name = 'Питомец'
    verbose_name_plural = 'Питомцы'


class VetCard(models.Model):
  pet = models.OneToOneField(
      Pet, on_delete=models.CASCADE, related_name='vet_card', verbose_name='Питомец'
  )
  last_checkup = models.DateField('Дата последнего осмотра')
  vaccinations = models.TextField('Прививки и обработки')
  diagnosis = models.TextField('Текущий диагноз / Особенности', blank=True, null=True)

  def __str__(self):
    return f'Веткарточка: {self.pet.name}'

  class Meta:
    verbose_name = 'Ветеринарная карточка'
    verbose_name_plural = 'Ветеринарные карточки'


class AdoptionApplication(models.Model):
  STATUS_CHOICES = [
      ('pending', 'На рассмотрении'),
      ('approved', 'Одобрена (ожидает договора)'),
      ('rejected', 'Отклонена'),
      ('completed', 'Договор подписан (обрёл дом)'),
  ]

  user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Кандидат')
  pet = models.ForeignKey(
      Pet, on_delete=models.CASCADE, related_name='applications', verbose_name='Питомец'
  )
  housing_conditions = models.TextField('Жилищные условия')
  experience = models.TextField('Опыт содержания животных')
  status = models.CharField('Статус заявки', max_length=20, choices=STATUS_CHOICES, default='pending')
  created_at = models.DateTimeField('Дата подачи', auto_now_add=True)

  def __str__(self):
    return f'Заявка #{self.id} от {self.user.username} на {self.pet.name}'

  class Meta:
    verbose_name = 'Анкета на усыновление'
    verbose_name_plural = 'Анкеты на усыновление'


class Interview(models.Model):
  application = models.OneToOneField(
      AdoptionApplication, on_delete=models.CASCADE,
      related_name='interview', verbose_name='Анкета',
  )
  curator = models.ForeignKey(
      User, on_delete=models.SET_NULL, null=True,
      related_name='curator_interviews', verbose_name='Куратор',
  )
  scheduled_time = models.DateTimeField('Дата и время собеседования')
  passed = models.BooleanField('Собеседование пройдено успешно', default=False)
  notes = models.TextField('Заметки куратора', blank=True, null=True)

  def __str__(self):
    return f'Собеседование по заявке #{self.application.id}'

  class Meta:
    verbose_name = 'Собеседование'
    verbose_name_plural = 'Собеседования'


class WalkingBooking(models.Model):
  volunteer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Волонтёр')
  pet = models.ForeignKey(
      Pet, on_delete=models.CASCADE, related_name='walks', verbose_name='Питомец'
  )
  date_time = models.DateTimeField('Дата и время прогулки')
  is_completed = models.BooleanField('Прогулка завершена', default=False)

  def __str__(self):
    return f'Прогулка с {self.pet.name} ({self.date_time})'

  class Meta:
    verbose_name = 'Запись на прогулку'
    verbose_name_plural = 'Записи на прогулки'


class AdoptionContract(models.Model):
  application = models.OneToOneField(
      AdoptionApplication, on_delete=models.CASCADE,
      related_name='contract', verbose_name='Анкета / Заявка',
  )
  signed_date = models.DateField('Дата подписания', auto_now_add=True)
  terms_agreed = models.BooleanField('Условия содержания приняты', default=True)

  def __str__(self):
    return f'Договор #{self.id} по питомцу {self.application.pet.name}'

  class Meta:
    verbose_name = 'Договор передачи'
    verbose_name_plural = 'Договоры передачи'


class SponsorshipPayment(models.Model):
  sponsor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Опекун')
  pet = models.ForeignKey(
      Pet, on_delete=models.CASCADE, related_name='sponsorships', verbose_name='Питомец'
  )
  amount = models.DecimalField('Сумма взноса (руб.)', max_digits=10, decimal_places=2)
  payment_date = models.DateTimeField('Дата платежа', auto_now_add=True)

  def __str__(self):
    return f'Взнос {self.amount} руб. от {self.sponsor.username} для {self.pet.name}'

  class Meta:
    verbose_name = 'Опекунский взнос'
    verbose_name_plural = 'Опекунские взносы'


class HomePhotoReport(models.Model):
  contract = models.ForeignKey(
      AdoptionContract, on_delete=models.CASCADE, related_name='reports', verbose_name='Договор'
  )
  report_date = models.DateField('Дата отчёта', auto_now_add=True)
  photo = models.ImageField('Фото из дома', upload_to='reports/')
  comment = models.TextField('Комментарий хозяина', blank=True, null=True)

  def __str__(self):
    return f'Отчёт по договору #{self.contract.id} от {self.report_date}'

  class Meta:
    verbose_name = 'Фотоотчёт из нового дома'
    verbose_name_plural = 'Фотоотчёты из нового дома'
