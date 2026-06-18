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

if __name__ == "__main__":
    test_carbon_estimate()
