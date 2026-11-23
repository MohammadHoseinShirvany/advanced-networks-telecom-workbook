
from __future__ import annotations


# Designed scenario inputs, in milliseconds (the same units as the HTML fields).
D_TP_MS = 2.0
D_P_MS = 12.0
D_TA_MS = 0.2
P = 0.08


def calculate_efficiency(
    d_tp_ms: float,
    d_p_ms: float,
    d_ta_ms: float,
    p: float,
    *,
    half_duplex: bool,
) -> dict[str, float | str]:
    """Apply the JavaScript formulas and return values in seconds and ms."""
    if not 0.0 <= p < 1.0:
        raise ValueError("P must satisfy 0 <= P < 1.")
    if min(d_tp_ms, d_p_ms, d_ta_ms) < 0.0:
        raise ValueError("Delay values must be non-negative.")

    # JavaScript lines 1608-1610: ms input converted to seconds.
    tp = d_tp_ms / 1000.0
    dp = d_p_ms / 1000.0
    ta = d_ta_ms / 1000.0

    # JavaScript lines 1613-1616, unchanged.
    s = tp + 2.0 * dp + ta
    timeout = s if half_duplex else tp
    expected_cycle = s + timeout * p / (1.0 - p)
    efficiency_percent = tp / expected_cycle * 100.0

    return {
        "mode": "Half-Duplex" if half_duplex else "Full-Duplex",
        "tp": tp,
        "dp": dp,
        "ta": ta,
        "s": s,
        "timeout": timeout,
        "expected_cycle": expected_cycle,
        "efficiency_percent": efficiency_percent,
    }


def print_result(result: dict[str, float | str]) -> None:
    """Print a detailed result for one duplex mode."""
    print(f"[{result['mode']}]")
    print("Inputs:")
    print(f"  D_TP = {D_TP_MS:.3f} ms")
    print(f"  D_P  = {D_P_MS:.3f} ms")
    print(f"  D_TA = {D_TA_MS:.3f} ms")
    print(f"  P    = {P:.3f}")
    print("Converted delays:")
    print(f"  tp = {result['tp']:.9f} s")
    print(f"  dp = {result['dp']:.9f} s")
    print(f"  ta = {result['ta']:.9f} s")
    print("Formulas:")
    print("  S = tp + 2 * dp + ta")
    print(f"    = {result['s'] * 1000:.3f} ms")
    print("  TO = S (Half-Duplex) or tp (Full-Duplex)")
    print(f"     = {result['timeout'] * 1000:.3f} ms")
    print("  EX = S + TO * P / (1 - P)")
    print(f"     = {result['expected_cycle'] * 1000:.6f} ms")
    print("  E = tp / EX * 100")
    print(f"    = {result['efficiency_percent']:.6f}%")
    print()


def main() -> None:
    print("Student Stop-and-Wait Efficiency Demo")
    print("Formula source: فصل 8 - شبکه .html, lines 1607-1623")
    print("=" * 56)
    for half_duplex in (False, True):
        result = calculate_efficiency(
            D_TP_MS,
            D_P_MS,
            D_TA_MS,
            P,
            half_duplex=half_duplex,
        )
        print_result(result)


if __name__ == "__main__":
    main()
