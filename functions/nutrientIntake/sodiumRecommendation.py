
def calculateSodium(total_sweat_loss_l,sex):
    
    sodium_mg = total_sweat_loss_l * 700
    
    if sex.lower() == 'female':
        sodium_mg *= 0.85

    return sodium_mg