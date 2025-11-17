
def calculateWaterIntake(total_sweat_loss_l,sex):
    
    water_ml = total_sweat_loss_l * 1000

    if sex.lower() == 'female':
        water_ml *= 0.9

    return water_ml