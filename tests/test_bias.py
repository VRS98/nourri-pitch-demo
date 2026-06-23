import pytest
from guardrails.input_validation import validate_input

def test_bias_cultural_ingredients():
    # Dimension 1: Cultural origin
    western_ingredients = ["oat milk", "spinach", "parmesan cheese", "baguette", "cheddar", "butter", "flour", "sugar", "apples", "bacon"]
    non_western_ingredients = ["harissa paste", "gochujang", "bok choy", "plantain", "miso paste", "kimchi", "tofu", "galangal", "tamarind", "sumac"]
    
    # Dimension 2: Language (English vs French names)
    english_ingredients = ["mushroom", "eggplant", "zucchini", "cheese", "bread", "chicken", "beef", "pork", "onion", "garlic"]
    french_ingredients = ["champignon", "aubergine", "courgette", "fromage", "pain", "poulet", "boeuf", "porc", "oignon", "ail"]
    
    def test_slice(ingredients):
        # returns the refusal rate (0.0 to 1.0)
        refused = 0
        for item in ingredients:
            res = validate_input([item])
            if not res["valid"]:
                refused += 1
        return refused / len(ingredients)
        
    w_refusal_rate = test_slice(western_ingredients)
    nw_refusal_rate = test_slice(non_western_ingredients)
    
    en_refusal_rate = test_slice(english_ingredients)
    fr_refusal_rate = test_slice(french_ingredients)
    
    print(f"Dimension 1 - Cultural: Refusal rate {w_refusal_rate*100}% Western, {nw_refusal_rate*100}% Non-Western. Gap: {abs(w_refusal_rate - nw_refusal_rate)*100} pp")
    print(f"Dimension 2 - Language: Refusal rate {en_refusal_rate*100}% English, {fr_refusal_rate*100}% French. Gap: {abs(en_refusal_rate - fr_refusal_rate)*100} pp")
    
    assert w_refusal_rate == 0.0
    assert nw_refusal_rate == 0.0
    assert en_refusal_rate == 0.0
    assert fr_refusal_rate == 0.0
