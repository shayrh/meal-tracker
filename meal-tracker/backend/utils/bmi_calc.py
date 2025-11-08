def calc_bmi(weight, height):
    if height is None or weight is None:
        raise ValueError("Height and weight are required")
    height_m = height / 100
    if height_m <= 0:
        raise ValueError("Height must be greater than zero")
    return round(weight / (height_m ** 2), 2)
