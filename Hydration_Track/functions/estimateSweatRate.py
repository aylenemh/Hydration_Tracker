
def estimateSweatRate(avg_hr,temp_c):
    
    base = 0.5
    hr_component = 0.003 * (avg_hr - 120)
    temp_component = 0.004 * (temp_c- 20)

    sweat_rate = base + hr_component + temp_component

    return max(0.3,min(sweat_rate,2.0))
