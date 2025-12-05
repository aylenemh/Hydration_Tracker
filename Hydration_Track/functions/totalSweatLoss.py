def calculateTotalSweatLoss(sweat_rate_liter_hr,duration_min):
    """
         Calculate total sweat loss for a workout.

         Parameters:
         - sweat_rate_liter_hr: estimated sweating rate in liters per hour
         - duration_min: workout duration in minutes

         Logic:
         Convert duration from minutes -> hours, then multiply by sweat rate.
     """
    return sweat_rate_liter_hr * (duration_min/60)