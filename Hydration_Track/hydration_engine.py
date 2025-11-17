from functions.estimateSweatRate import estimateSweatRate
from functions.totalSweatLoss import calculateTotalSweatLoss
from functions.waterIntake import calculateWaterIntake

from functions.nutrientIntake.magnesiumRecommendation import calculateMagnesium
from functions.nutrientIntake.potassiumRecommendation import calculatePotassium
from functions.nutrientIntake.sodiumRecommendation import calculateSodium

from functions.temperatureFactor import temperatureFactor


def hydration_engine(weight, sex, duration_min, heart_rate, temp_c=22):
    
    sweat_rate = estimateSweatRate(heart_rate, temp_c)
    total_sweat_loss = calculateTotalSweatLoss(sweat_rate, duration_min)

    water_ml = calculateWaterIntake(total_sweat_loss, sex)
    sodium_mg = calculateSodium(total_sweat_loss, sex)
    potassium_mg = calculatePotassium(total_sweat_loss)
    magnesium_mg = calculateMagnesium(total_sweat_loss)

    results = {
        "water_ml": water_ml,
        "sodium_mg": sodium_mg,
        "potassium_mg": potassium_mg,
        "magnesium_mg": magnesium_mg,
        "sweat_rate_L_per_hr": sweat_rate,
        "total_sweat_loss_L": total_sweat_loss
    }

    return temperatureFactor(results, temp_c)