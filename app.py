
# ==========================================
# OMEGA WHEEL-DISTANCE ENGINE
# LEAKAGE-CHECKED SCIENTIFIC VERSION
# RAILWAY READY
# ==========================================

import re
import csv
from math import log2
from collections import defaultdict

# ==========================================
# HARDCODED SETTINGS
# ==========================================

WINDOW_SIZE = 4

MIN_CONFIDENCE = 0.75

KILL_STREAK = 3

BET_SIZE = 7

WIN_RETURN = 29

SECTOR_RADIUS = 2

# ==========================================
# WHEEL MODE
# ==========================================

USE_WHEEL_DISTANCE = True

# ==========================================
# EUROPEAN WHEEL ORDER
# ==========================================

wheel = [

    0, 32, 15, 19, 4, 21, 2, 25, 17, 34,
    6, 27, 13, 36, 11, 30, 8, 23, 10,
    5, 24, 16, 33, 1, 20, 14, 31, 9,
    22, 18, 29, 7, 28, 12, 35, 3, 26

]

wheel_pos = {n: i for i, n in enumerate(wheel)}

# ==========================================
# PARSER
# ==========================================

def parse_spins(text):

    nums = [int(x) for x in re.findall(r"\d+", text)]

    return [n for n in nums if 0 <= n <= 36]

# ==========================================
# WHEEL SECTOR FUNCTION
# ==========================================

def get_wheel_sector(number, radius=2):

    idx = wheel_pos[number]

    sector = []

    for offset in range(-radius, radius + 1):

        sector.append(
            wheel[(idx + offset) % len(wheel)]
        )

    return sector

# ==========================================
# TRUE SHANNON ENTROPY
# ==========================================

def calculate_entropy(window):

    counts = {}

    for n in window:

        counts[n] = counts.get(n, 0) + 1

    total = len(window)

    entropy = 0

    for c in counts.values():

        p = c / total

        entropy -= p * log2(p)

    return round(entropy, 4)

# ==========================================
# ENGINE
# ==========================================

def run_engine(spins):

    if len(spins) < WINDOW_SIZE:

        print("Not enough spins.")
        return

    bets = 0
    wins = 0
    losses = 0

    bankroll = 0

    total_risk = 0

    current_losing_streak = 0
    max_losing_streak = 0

    valid_signals = 0

    # ==========================================
    # DIAGNOSTICS
    # ==========================================

    fail_reasons = defaultdict(int)

    signal_log = []

    # ==========================================
    # MAIN LOOP
    # ==========================================

    for i in range(WINDOW_SIZE, len(spins)):

        window = spins[i - WINDOW_SIZE:i]

        actual = spins[i]

        counts = {}

        for n in window:

            counts[n] = counts.get(n, 0) + 1

        dominant = max(counts, key=counts.get)

        confidence = counts[dominant] / WINDOW_SIZE

        entropy_score = calculate_entropy(window)

        # ==========================================
        # FILTERS
        # ==========================================

        if current_losing_streak >= KILL_STREAK:

            fail_reasons["kill_streak"] += 1

            current_losing_streak = 0

            continue

        if confidence < MIN_CONFIDENCE:

            fail_reasons["low_confidence"] += 1
            continue

        cluster_hits = window.count(window[-1])

        if cluster_hits < 2:

            fail_reasons["weak_cluster"] += 1
            continue

        if len(set(window)) > 3:

            fail_reasons["high_uniqueness"] += 1
            continue

        if spins[i - 1] != dominant:

            fail_reasons["momentum_fail"] += 1
            continue

        # ==========================================
        # SIGNAL
        # ==========================================

        valid_signals += 1

        # ==========================================
        # WHEEL-DISTANCE SECTOR
        # ==========================================

        if USE_WHEEL_DISTANCE:

            sector = get_wheel_sector(
                dominant,
                SECTOR_RADIUS
            )

        else:

            sector = [

                (dominant - SECTOR_RADIUS) % 37,
                (dominant - 1) % 37,
                dominant,
                (dominant + 1) % 37,
                (dominant + SECTOR_RADIUS) % 37

            ]

        bets += 1

        total_risk += BET_SIZE

        print("=" * 50)

        print(f"Spin Index: {i}")

        print(f"Window: {window}")

        print(f"Dominant: {dominant}")

        print(f"Confidence: {round(confidence, 2)}")

        print(f"Entropy Score: {entropy_score}")

        print(f"Sector Bet: {sector}")

        print(f"Actual: {actual}")

        # ==========================================
        # RESULT
        # ==========================================

        if actual in sector:

            outcome = "WIN"

            wins += 1

            bankroll += WIN_RETURN

            current_losing_streak = 0

        else:

            outcome = "LOSS"

            losses += 1

            bankroll -= BET_SIZE

            current_losing_streak += 1

            max_losing_streak = max(
                max_losing_streak,
                current_losing_streak
            )

        print(f"RESULT: {outcome}")

        print(f"Bankroll: {bankroll}")

        # ==========================================
        # STORE SIGNAL
        # ==========================================

        signal_log.append({

            "index": i,
            "window": window,
            "dominant": dominant,
            "confidence": round(confidence, 2),
            "entropy": entropy_score,
            "sector": sector,
            "actual": actual,
            "result": outcome,
            "bankroll": bankroll

        })

    # ==========================================
    # SESSION STATUS
    # ==========================================

    if valid_signals <= 1:

        session_status = "DEAD — LEAVE"

    elif valid_signals == 2:

        session_status = "WEAK — CAUTION"

    else:

        session_status = "ACTIVE — TRADE"

    win_rate = (
        wins / bets * 100
        if bets else 0
    )

    roi = (
        bankroll / total_risk * 100
        if total_risk else 0
    )

    expectancy = (
        ((wins / bets) * WIN_RETURN)
        -
        ((losses / bets) * BET_SIZE)
    ) if bets else 0

    # ==========================================
    # FINAL OUTPUT
    # ==========================================

    print("\n")
    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)

    print(f"Total Spins: {len(spins)}")

    print(f"Signals: {valid_signals}")

    print(f"Session: {session_status}")

    print(f"Bets: {bets}")

    print(f"Wins: {wins}")

    print(f"Losses: {losses}")

    print(f"Win Rate: {round(win_rate, 2)}%")

    print(f"Bankroll: {bankroll}")

    print(f"ROI: {round(roi, 2)}%")

    print(f"Expectancy Per Trade: {round(expectancy, 2)}")

    print(f"Total Risk: {total_risk}")

    print(f"Max Losing Streak: {max_losing_streak}")

    # ==========================================
    # FAIL REASONS
    # ==========================================

    print("\n")
    print("=" * 50)
    print("FAIL REASONS")
    print("=" * 50)

    for reason, count in fail_reasons.items():

        print(f"{reason}: {count}")

    # ==========================================
    # SIGNAL LOG
    # ==========================================

    print("\n")
    print("=" * 50)
    print("SIGNAL LOG")
    print("=" * 50)

    for s in signal_log:

        print(s)

    # ==========================================
    # CSV EXPORT
    # ==========================================

    with open("omega_signal_log.csv", "w", newline="") as f:

        writer = csv.DictWriter(

            f,

            fieldnames=[
                "index",
                "window",
                "dominant",
                "confidence",
                "entropy",
                "sector",
                "actual",
                "result",
                "bankroll"
            ]
        )

        writer.writeheader()

        for row in signal_log:

            writer.writerow(row)

    print("\nCSV EXPORT COMPLETE:")
    print("omega_signal_log.csv")

# ==========================================
# INPUT
# ==========================================

raw_data = """
PASTE SPINS HERE
"""

spins = parse_spins(raw_data)

# ==========================================
# RUN
# ==========================================

run_engine(spins)
