# Edge Case (Fallback)

**Input**: `["harissa paste"]`

**Execution**:
1. **Agent Step 1**: Received input `["harissa paste"]`. Decision: Check local producers first.
2. **Tool Call**: `check_local_producer("harissa paste")`
3. **Tool Output**: `{"available": false}`
4. **Agent Step 2**: Item not found locally. Fallback triggered. Decision: Check supermarket fallback.
5. **Tool Call**: `check_supermarket_fallback("harissa paste")`
6. **Tool Output**: `{"available": true, "price": 2.10, "source": "Carrefour", "channel": "supermarket"}`
7. **Agent Step 3**: Item sourced. Compile cart and calculate total.
8. **Cart Compilation**: `total_price = 2.10`. Wait for human approval. for user approval.
