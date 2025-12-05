def estimateSweatRate(avg_hr, temp_c):
    """
        Estimate sweat rate (L/hr) based on heart rate and temperature.
        Model assumptions:
          - Base sweat rate is 0.5 L/hr for moderate exercise at ~120 bpm and 20°C.
          - For every 1 bpm above 120, sweat rate increases slightly (0.003 L/hr).
          - For every 1°C above 20°C, sweat rate increases (0.004 L/hr).
          - Final sweat rate is clamped between 0.3 and 2.0 L/hr to avoid unrealistic values.

        This provides a simplified but physiologically reasonable estimate of sweat loss.
    """

    base = 0.5                                            # baseline sweat rate at neutral conditions
    hr_component = 0.003 * (avg_hr - 120)                 # increased sweat rate from higher intensity
    temp_component = 0.004 * (temp_c - 20)                # increased sweat rate from hotter temperature

    sweat_rate = base + hr_component + temp_component

    # Constrain output to physiologically reasonable limits
    return max(0.3, min(sweat_rate, 2.0))
