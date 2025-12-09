
def calculateSodium(total_sweat_loss_l,sex):
# Base sodium loss estimate: ~700 mg per liter of sweat
    sodium_mg = total_sweat_loss_l * 700
# Females typically lose slightly less sodium per liter of sweat   
    if sex.lower() == 'female':
        sodium_mg *= 0.85

    return sodium_mg