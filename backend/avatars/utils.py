def get_age_range(age):
    """
    Convert selected age into predefined age ranges
    """

    age = int(age)

    if 18 <= age <= 25:
        return "18-25"
    elif 26 <= age <= 35:
        return "26-35"
    elif 36 <= age <= 45:
        return "36-45"
    elif 46 <= age <= 55:
        return "46-55"
    else:
        return "56-70"