
def calculateWaterIntake(total_sweat_loss_l, sex):
   
    # Convert total sweat loss from liters to milliliters
    water_ml = total_sweat_loss_l * 1000

    # Females generally require slightly less fluid for same sweat loss
    if sex.lower() == 'female':
        water_ml *= 0.9

    # Return final recommended water intake in mL
    return water_ml
