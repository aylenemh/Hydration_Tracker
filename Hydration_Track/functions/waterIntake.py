
def calculateWaterIntake(total_sweat_loss_l,sex):
    """
        Convert total sweat loss (in liters) into recommended water intake (in mL).

        Assumptions:
        - 1 L sweat loss ≈ 1000 mL fluid replacement.
        - Female athletes may have slightly lower total replacement needs,
          so we apply a 0.9 adjustment factor (a conservative physiological assumption).
    """
    water_ml = total_sweat_loss_l * 1000

    if sex.lower() == 'female':
        water_ml *= 0.9

    return water_ml