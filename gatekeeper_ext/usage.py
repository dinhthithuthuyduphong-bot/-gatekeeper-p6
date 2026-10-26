"""Token accounting that survives the way Vertex reports thinking models.  Standard library only.

Observed in the smoke test of 26/10/2026 (model google/gemini-3.1-pro-preview, reasoning_effort low):
    {"prompt_tokens": 7, "total_tokens": 19, "completion_tokens_details": {"reasoning_tokens": 12}}
there is NO completion_tokens field, and the thinking tokens are only in total_tokens.  The flash model reported
    {"prompt_tokens": 7, "completion_tokens": 1, "total_tokens": 8}.
The provider's own total is the safest measure of what is billed as output, so output = total - prompt when both exist.
"""


def output_tokens(usage):
    """Tokens billed as output (visible answer plus thinking), or None if the usage record cannot tell."""
    if not usage:
        return None
    total, prompt = usage.get("total_tokens"), usage.get("prompt_tokens")
    if isinstance(total, int) and isinstance(prompt, int) and total >= prompt:
        return total - prompt
    if isinstance(usage.get("completion_tokens"), int):
        return usage["completion_tokens"]
    reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
    return reasoning if isinstance(reasoning, int) else None


def reasoning_tokens(usage):
    return ((usage or {}).get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0
