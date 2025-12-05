from functions.estimateSweatRate import estimateSweatRate
from functions.totalSweatLoss import calculateTotalSweatLoss
from functions.waterIntake import calculateWaterIntake

from functions.nutrientIntake.magnesiumRecommendation import calculateMagnesium
from functions.nutrientIntake.potassiumRecommendation import calculatePotassium
from functions.nutrientIntake.sodiumRecommendation import calculateSodium

from functions.temperatureFactor import temperatureFactor


def hydration_engine(weight, sex, duration_min, heart_rate, temp_c=22):
    """
        Core hydration calculation engine.
        Combines sweat-rate estimation, total fluid loss, and electrolyte needs
        into a single structured output used by the application.

        Parameters:
            weight (float): User weight in kg.
            sex (str): 'male' or 'female'; affects water + sodium adjustments.
            duration_min (float): Workout duration in minutes.
            heart_rate (float): Avg. HR during workout.
            temp_c (float): Ambient temperature (°C), default = 22°C.

        Returns:
            dict: Contains water needed (ml), sodium/potassium/magnesium losses,
                  sweat rate, total sweat loss, all optionally adjusted for heat.
    """

    # ---------------------------------------------------------
    # 1. Estimate sweat rate based on HR + temperature
    # ---------------------------------------------------------
    # Sweat rate (L/hr) increases with higher HR or hotter conditions.
    sweat_rate = estimateSweatRate(heart_rate, temp_c)

    # ---------------------------------------------------------
    # 2. Total sweat loss (L)
    # ---------------------------------------------------------
    # Converts sweat rate (L/hr) into total volume lost based on workout time.
    total_sweat_loss = calculateTotalSweatLoss(sweat_rate, duration_min)

    # ---------------------------------------------------------
    # 3. Fluid requirements (water needed in mL)
    # ---------------------------------------------------------
    # Females are adjusted slightly down because average sweat sodium content differs.
    water_ml = calculateWaterIntake(total_sweat_loss, sex)

    # ---------------------------------------------------------
    # 4. Electrolyte losses (mg)
    # ---------------------------------------------------------
    # Sodium loss is strongly dependent on sweat rate + sex.
    sodium_mg = calculateSodium(total_sweat_loss, sex)

    # Potassium is proportional to total sweat volume.
    potassium_mg = calculatePotassium(total_sweat_loss)

    # Magnesium is lost in small quantities and also depends on sweat volume.
    magnesium_mg = calculateMagnesium(total_sweat_loss)

    # ---------------------------------------------------------
    # 5. Bundle the raw results before heat adjustment
    # ---------------------------------------------------------
    results = {
        "water_ml": water_ml,
        "sodium_mg": sodium_mg,
        "potassium_mg": potassium_mg,
        "magnesium_mg": magnesium_mg,
        "sweat_rate_L_per_hr": sweat_rate,
        "total_sweat_loss_L": total_sweat_loss
    }

    # ---------------------------------------------------------
    # 6. Apply temperature multiplier (hot-weather adjustment)
    # ---------------------------------------------------------
    # If it's hot outside, all hydration + electrolyte needs increase.
    return temperatureFactor(results, temp_c)