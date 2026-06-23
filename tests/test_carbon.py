# Carbon Footprint Test
# In an offline environment without an LLM key, we estimate tokens based on known prompt sizes.

def test_carbon_estimate():
    # A typical agent run uses ~1500 input tokens and ~300 output tokens.
    avg_tokens_per_task = 1800
    
    # 1 token roughly uses 0.000000004 kWh (for average models)
    kwh_per_token = 4e-9
    kwh_per_task = avg_tokens_per_task * kwh_per_token
    
    # Grid intensity (EU average ~ 250 gCO2eq/kWh)
    gco2_per_task = kwh_per_task * 250
    
    # Monthly projection at 10,000 tasks
    monthly_tasks = 10000
    monthly_gco2 = gco2_per_task * monthly_tasks
    
    assert gco2_per_task < 0.1 # Very small per task
    print(f"Tokens per task: {avg_tokens_per_task}")
    print(f"gCO2eq per task: {gco2_per_task:.6f}")
    print(f"Monthly gCO2eq: {monthly_gco2:.2f}")

    print("\n--- Model Carbon Comparison Table ---")
    print(f"{'Model':<20} | {'Tokens/Task':<12} | {'kWh/Task':<15} | {'gCO2eq/Task':<15} | {'Monthly gCO2eq'}")
    print("-" * 85)
    # Gemini 2.0 Flash row
    print(f"{'Gemini 2.0 Flash':<20} | {avg_tokens_per_task:<12} | {kwh_per_task:<15.8f} | {gco2_per_task:<15.6f} | {monthly_gco2:<10.2f}")
    # SLM (e.g., Llama 3 8B) row - estimated tokens could be similar, but energy per token depends on hardware.
    # Assuming SLM uses slightly less tokens or similar, but run locally (0 network cost, maybe 3e-9 kWh/token)
    slm_tokens = 1500
    slm_kwh = slm_tokens * 3e-9
    slm_gco2 = slm_kwh * 250
    slm_monthly = slm_gco2 * monthly_tasks
    print(f"{'SLM (Llama 3 8B)':<20} | {slm_tokens:<12} | {slm_kwh:<15.8f} | {slm_gco2:<15.6f} | {slm_monthly:<10.2f}")
    print("-" * 85)

if __name__ == "__main__":
    test_carbon_estimate()
