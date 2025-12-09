def calculateTotalSweatLoss(sweat_rate_liter_hr, duration_min):
  
    # Convert duration from minutes to hours and multiply by sweat rate
    return sweat_rate_liter_hr * (duration_min / 60)
