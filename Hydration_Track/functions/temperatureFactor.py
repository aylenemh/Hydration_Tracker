
def temperatureFactor(recommendations,temp_c):

    if temp_c >= 35:
        multiplier = 1.25
    elif temp_c >= 30:
        multiplier = 1.15
    else: 
        multiplier = 1.0

    for key in recommendations:
        recommendations[key] *= multiplier
    
    return recommendations