from .models import Avatar


def find_matching_avatar(gender, age, ethnicity, hair_style):

    avatar = Avatar.objects.filter(
        avatar_type="ai",
        gender=gender,
        age_range=age,
        ethnicity=ethnicity,
        hair_style=hair_style,
        avatar_image__isnull=False
    ).first()

    return avatar