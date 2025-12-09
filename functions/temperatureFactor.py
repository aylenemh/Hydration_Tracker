
def temperatureFactor(recommendations, temp_c):
    # Determine the multiplier based on temperature ranges
    if temp_c >= 35:
        multiplier = 1.25   # Very hot conditions → +25% increase
    elif temp_c >= 30:
        multiplier = 1.15   # Hot conditions → +15% increase
    else:
        multiplier = 1.0    # Normal temperatures → no adjustment

    # Apply the multiplier to every recommendation value
    for key in recommendations:
        recommendations[key] *= multiplier

    # Return the updated recommendation dictionary
    return recommendations
