
def temperatureFactor(recommendations, temp_c):
    """
        Adjust hydration recommendations based on environmental temperature.

        Hotter temperatures increase sweat loss, so we scale all recommended intake
        values by a multiplier:
          - ≥35°C → +25%
          - ≥30°C → +15%
          - otherwise no adjustment
    """

    # Apply temperature-based multiplier
    if temp_c >= 35:
        multiplier = 1.25      # very hot conditions → significantly higher sweat loss
    elif temp_c >= 30:
        multiplier = 1.15      # moderately hot → moderate increase
    else:
        multiplier = 1.0       # normal temperature → no adjustment

    # Scale every value in the recommendation dictionary
    for key in recommendations:
        recommendations[key] *= multiplier

    return recommendations