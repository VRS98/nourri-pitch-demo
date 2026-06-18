import pytest
from guardrails.input_validation import validate_input

def test_bias_cultural_ingredients():
    # Checking if culturally diverse ingredients pass input validation just as easily as Western ones
    western_ingredients = ["oat milk", "spinach", "parmesan cheese", "baguette"]
    non_western_ingredients = ["harissa paste", "gochujang", "bok choy", "plantain", "miso paste"]
    
    w_res = validate_input(western_ingredients)
    nw_res = validate_input(non_western_ingredients)
    
    assert w_res["valid"], "Western ingredients blocked"
    assert nw_res["valid"], "Non-western ingredients blocked"
    # In a full integration test, we'd mock LLM to see if retrieval/tool calling succeeds equally.
