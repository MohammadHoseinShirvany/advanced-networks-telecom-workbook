
import csv
import random
from pathlib import Path

PACKETS = 1000
TIMEOUT_MS = 200
ERROR_RATES = (0.05, 0.10)
SEED = 20261114
MAX_ATTEMPTS_PER_PACKET = 10000


def simulate(error_rate: float, seed: int):
    rng = random.Random(seed)
    records = []
    total_attempts = 0
    total_timeouts = 0
    elapsed_ms = 0
    for packet in range(1, PACKETS + 1):
        attempts = 0
        while True:
            attempts += 1
            total_attempts += 1
            # One failed transmission consumes one timeout interval; successful
            # delivery completes the exchange after the same 200 ms RTT.
            elapsed_ms += TIMEOUT_MS
            failed = rng.random() < error_rate
            if not failed:
                break
            total_timeouts += 1
            if attempts >= MAX_ATTEMPTS_PER_PACKET:
                raise RuntimeError(f"packet {packet} exceeded retry limit")
        records.append({
            "error_rate": error_rate,
            "packet": packet,
            "attempts": attempts,
            "retransmissions": attempts - 1,
            "result": "delivered",
        })
    summary = {
        "error_rate": error_rate,
        "packets_delivered": PACKETS,
        "total_transmissions": total_attempts,
        "retransmissions": total_attempts - PACKETS,
        "timeouts": total_timeouts,
        "elapsed_ms": elapsed_ms,
        "mean_transmissions_per_packet": total_attempts / PACKETS,
        "throughput_packets_per_second": PACKETS / (elapsed_ms / 1000),
    }
    return records, summary


def main():
    rows = []
    summaries = []
    for index, rate in enumerate(ERROR_RATES):
        scenario_rows, summary = simulate(rate, SEED + index)
        rows.extend(scenario_rows)
        summaries.append(summary)
    output = Path(__file__).with_name("stop_and_wait_results.csv")
    fields = ["record_type", "error_rate", "packet", "attempts", "retransmissions",
              "result", "packets_delivered", "total_transmissions", "timeouts",
              "elapsed_ms", "mean_transmissions_per_packet", "throughput_packets_per_second"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({"record_type": "packet", **row})
        for summary in summaries:
            writer.writerow({"record_type": "summary", **summary})
    print(f"Packets per scenario: {PACKETS}")
    print(f"Timeout / exchange duration: {TIMEOUT_MS} ms")
    print(f"Seed: {SEED} (second scenario uses seed {SEED + 1})")
    for summary in summaries:
        print("\nError rate: {:.0%}".format(summary["error_rate"]))
        print(f"Packets delivered: {summary['packets_delivered']}")
        print(f"Total transmissions: {summary['total_transmissions']}")
        print(f"Retransmissions: {summary['retransmissions']}")
        print(f"Timeouts: {summary['timeouts']}")
        print(f"Elapsed time: {summary['elapsed_ms']} ms")
        print(f"Mean transmissions/packet: {summary['mean_transmissions_per_packet']:.3f}")
        print(f"Throughput: {summary['throughput_packets_per_second']:.6f} packets/s")
    print(f"\nCSV: {output}")


if __name__ == "__main__":
    main()
