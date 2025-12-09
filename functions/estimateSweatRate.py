def estimateSweatRate(avg_hr, temp_c):
    
    # Base sweat rate (L/hr) at normal resting conditions
    base = 0.5

    # Heart-rate component:
    # For every 1 bpm above 120, add 0.003 L/hr
    hr_component = 0.003 * (avg_hr - 120)

    # Temperature component:
    # For every 1°C above 20°C, add 0.004 L/hr
    temp_component = 0.004 * (temp_c - 20)

    # Combine components to estimate sweat rate
    sweat_rate = base + hr_component + temp_component

    # Clamp value to the safe physiological range: 0.3–2.0 L/hr
    return max(0.3, min(sweat_rate, 2.0))

