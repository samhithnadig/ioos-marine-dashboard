import random

# ==============================================================================
# NOAAs EnsemblePerturbation NATIVE SURROGATE MODULE
# This script fulfills GSoC Issue #113 by running hurricane tracking 
# regressions using ZERO external mathematical dependencies.
# ==============================================================================

# 1. Baseline Hurricane Attributes
baseline_forecast = {
    "storm_name": "Hurricane Laura-Sim",
    "max_wind_speed_knots": 130.0,
    "central_pressure_mb": 937.0
}

# 2. Simulated Heavy Hydrodynamic Model (Acts as our training reference)
def calculate_true_surge(wind, pressure):
    """
    Simulates sea-surface elevation response. In production, this replaces 
    running a heavy server-side hydrodynamic simulation model.
    """
    pressure_drop = 1013.0 - pressure
    return round((0.0002 * (wind ** 2)) + (0.04 * pressure_drop), 2)

# 3. Ensemble Generation Step
def generate_perturbed_ensemble(base, sample_size=6):
    """
    Perturbs baseline parameters to create an ensemble training array.
    """
    ensemble = []
    print(f"📦 Simulating {sample_size} perturbed hurricane track iterations...")
    
    for i in range(sample_size):
        perturbed_wind = base["max_wind_speed_knots"] + random.uniform(-15, 15)
        perturbed_pressure = base["central_pressure_mb"] + random.uniform(-10, 10)
        surge = calculate_true_surge(perturbed_wind, perturbed_pressure)
        
        ensemble.append({
            "run_id": f"RUN_{i+1:03d}",
            "wind": round(perturbed_wind, 1),
            "pressure": round(perturbed_pressure, 1),
            "surge_prediction_m": surge
        })
    return ensemble

# 4. Clean, Dependency-Free Multi-Variable Regression
def train_surrogate_coefficients(training_data):
    """
    Replaces chaospy.fit_regression by calculating relationship weightings
    between wind speed vectors, pressure drops, and peak coastal surge.
    """
    print("\n🧮 Fitting lightweight multi-variable surrogate model...")
    n = len(training_data)
    if n == 0: return 0, 0, 0

    # Calculate means
    mean_wind = sum(r["wind"] for r in training_data) / n
    mean_pressure = sum(r["pressure"] for r in training_data) / n
    mean_surge = sum(r["surge_prediction_m"] for r in training_data) / n

    # Calculate variances and covariances manually without numpy or chaospy
    var_wind = sum((r["wind"] - mean_wind) ** 2 for r in training_data) / n
    var_pressure = sum((r["pressure"] - mean_pressure) ** 2 for r in training_data) / n
    
    cov_wind_surge = sum((r["wind"] - mean_wind) * (r["surge_prediction_m"] - mean_surge) for r in training_data) / n
    cov_press_surge = sum((r["pressure"] - mean_pressure) * (r["surge_prediction_m"] - mean_surge) for r in training_data) / n

    # Derive clean sensitivity weight coefficients (slopes)
    weight_wind = cov_wind_surge / var_wind if var_wind != 0 else 0
    weight_pressure = cov_press_surge / var_pressure if var_pressure != 0 else 0
    
    # Calculate the base intercept
    intercept = mean_surge - (weight_wind * mean_wind) - (weight_pressure * mean_pressure)

    return weight_wind, weight_pressure, intercept

# ==============================================================================
# OPERATION RUNNER
# ==============================================================================
if __name__ == "__main__":
    print(f"=== INITIALIZING SURROGATE MODEL PIPELINE FOR {baseline_forecast['storm_name'].upper()} ===")
    
    # Generate data matrix
    dataset = generate_perturbed_ensemble(baseline_forecast, sample_size=6)
    for run in dataset:
        print(f"  [{run['run_id']}] Wind: {run['wind']} kts | Pressure: {run['pressure']} mb -> Surge: {run['surge_prediction_m']}m")
        
    # Extract surrogate physics formula
    w_wind, w_press, b = train_surrogate_coefficients(dataset)
    print(f"✅ Surrogate Formula Derived: Surge = ({w_wind:.4f} * Wind) + ({w_press:.4f} * Pressure) + ({b:.4f})")
    
    # Run instant surrogate prediction test
    test_wind = 145.0
    test_press = 920.0
    fast_prediction = (w_wind * test_wind) + (w_press * test_press) + b
    print(f"\n⚡ INSTANT SURROGATE INFERENCE TEST:")
    print(f"   Predicting surge for Category 4 surge spike ({test_wind} kts, {test_press} mb): {fast_prediction:.2f} meters!")
    