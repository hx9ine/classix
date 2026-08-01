from django.db import models


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


# Future shared enums can live here, for example:
#
# class BloodGroup(models.TextChoices):
#     ...
#
# class Country(models.TextChoices):
#     ...
#
# class Language(models.TextChoices):
#     ...