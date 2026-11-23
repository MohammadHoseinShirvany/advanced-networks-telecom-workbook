
import csv
import random
from pathlib import Path

# Section 3's equations do not prescribe numerical link timings; these are
# explicit, editable example defaults, in milliseconds.
P_ERROR = 0.10
P_ACK_LOSS = 0.05
N_PACKETS = 1000
D_TP_MS = 1.0       # packet transmission duration
D_P_MS = 10.0       # one-way propagation delay
D_TA_MS = 0.1       # ACK transmission duration
TO_MS = 2 * D_P_MS + D_TP_MS + D_TA_MS  # one round-trip exchange time
SEED = 20261114
MAX_ATTEMPTS_PER_PACKET = 10000


def simulate():
    rng = random.Random(SEED)
    rows = []
    total_time_ms = 0.0
    total_tx = total_retx = data_errors = ack_losses = 0
    for packet in range(1, N_PACKETS + 1):
        attempts = 0
        packet_time = 0.0
        while True:
            attempts += 1
            total_tx += 1
            if rng.random() < P_ERROR:
                data_errors += 1
                packet_time += TO_MS
            elif rng.random() < P_ACK_LOSS:
                ack_losses += 1
                packet_time += TO_MS
            else:
                packet_time += D_TP_MS + 2 * D_P_MS + D_TA_MS
                break
            if attempts >= MAX_ATTEMPTS_PER_PACKET:
                raise RuntimeError(f"packet {packet} exceeded retry limit")
        total_retx += attempts - 1
        total_time_ms += packet_time
        rows.append({"record_type": "packet", "packet": packet,
                     "attempts": attempts, "retransmissions": attempts - 1,
                     "elapsed_ms": round(packet_time, 6), "result": "delivered"})

    p_fail = 1 - (1 - P_ERROR) * (1 - P_ACK_LOSS)
    s_ms = D_TP_MS + 2 * D_P_MS + D_TA_MS
    expected_x_ms = s_ms + TO_MS * p_fail / (1 - p_fail)
    summary = {
        "record_type": "summary", "p_error": P_ERROR,
        "p_ack_loss": P_ACK_LOSS, "p_exchange_failure": p_fail,
        "n_packets": N_PACKETS, "D_TP_ms": D_TP_MS, "D_P_ms": D_P_MS,
        "D_TA_ms": D_TA_MS, "TO_ms": TO_MS, "S_ms": s_ms,
        "expected_X_ms": expected_x_ms, "data_errors": data_errors,
        "ack_losses": ack_losses, "total_transmissions": total_tx,
        "retransmissions": total_retx, "total_elapsed_ms": round(total_time_ms, 6),
        "mean_elapsed_ms_per_packet": total_time_ms / N_PACKETS,
        "theoretical_efficiency": D_TP_MS / expected_x_ms,
        "empirical_efficiency": N_PACKETS * D_TP_MS / total_time_ms,
        "throughput_packets_per_second": N_PACKETS / (total_time_ms / 1000),
        "seed": SEED,
    }
    rows.append(summary)
    return rows, summary


def main():
    rows, s = simulate()
    output = Path(__file__).with_name("stop_and_wait_section3_results.csv")
    fields = ["record_type", "packet", "attempts", "retransmissions", "elapsed_ms",
              "result", "p_error", "p_ack_loss", "p_exchange_failure", "n_packets",
              "D_TP_ms", "D_P_ms", "D_TA_ms", "TO_ms", "S_ms", "expected_X_ms",
              "data_errors", "ack_losses", "total_transmissions", "total_elapsed_ms",
              "mean_elapsed_ms_per_packet", "theoretical_efficiency", "empirical_efficiency",
              "throughput_packets_per_second", "seed"]
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {N_PACKETS} packet records and one summary: {output}")
    for key in ("S_ms", "TO_ms", "expected_X_ms", "total_transmissions",
                "total_elapsed_ms", "theoretical_efficiency", "empirical_efficiency",
                "throughput_packets_per_second"):
        print(f"{key}={s[key]}")


if __name__ == "__main__":
    main()
