"""Generate a realistic synthetic dataset of 200 off-road trails -> data/trails.csv"""
import csv
import os
import random

random.seed(42)

# Real off-road / overlanding states weighted toward big trail states
STATES = [
    "Colorado", "Utah", "Arizona", "California", "Nevada", "Montana",
    "Wyoming", "New Mexico", "Idaho", "Oregon", "Washington", "Texas",
    "Tennessee", "North Carolina", "West Virginia", "Michigan",
    "Pennsylvania", "Georgia", "Oklahoma", "Minnesota",
]
STATE_WEIGHTS = [
    16, 16, 12, 10, 8, 5, 5, 5, 4, 4, 4, 5, 4, 4, 3, 3, 3, 2, 2, 2,
]

TRAIL_TYPES = ["Forest", "Desert", "Mountain", "Rock Crawling", "Mud", "Scenic"]

# Descriptive name parts
PREFIXES = [
    "Eagle", "Bear", "Devil's", "Red Rock", "Ghost", "Iron", "Lost",
    "Granite", "Coyote", "Thunder", "Rattlesnake", "Hidden", "Black",
    "Silver", "Cedar", "Pine", "Copper", "Wild Horse", "Broken", "Stone",
    "Timber", "Boulder", "Cottonwood", "Juniper", "Sand", "Cliff",
    "Canyon", "Summit", "Frost", "Buffalo",
]
SUFFIXES = [
    "Pass", "Ridge", "Trail", "Canyon", "Gulch", "Loop", "Run", "Crossing",
    "Basin", "Ledge", "Notch", "Flats", "Mesa", "Hollow", "Draw", "Spur",
    "Rim", "Grade", "Fork", "Wash", "Saddle", "Bench",
]

# Difficulty -> plausible vehicle requirements (weighted)
VEHICLE_BY_DIFF = {
    "Easy":     (["Any SUV", "Stock Jeep"], [80, 20]),
    "Moderate": (["Any SUV", "Stock Jeep", "Lifted Jeep"], [30, 50, 20]),
    "Hard":     (["Stock Jeep", "Lifted Jeep", "Locker Required"], [15, 55, 30]),
    "Extreme":  (["Lifted Jeep", "Locker Required"], [30, 70]),
}

# Difficulty -> rough length range (miles), elevation gain (ft), scenic baseline
LENGTH_BY_DIFF = {
    "Easy":     (1.5, 12.0),
    "Moderate": (2.0, 18.0),
    "Hard":     (1.0, 14.0),
    "Extreme":  (0.5, 8.0),
}
ELEV_BY_DIFF = {
    "Easy":     (50, 900),
    "Moderate": (300, 2200),
    "Hard":     (600, 3500),
    "Extreme":  (800, 4500),
}

DIFFICULTIES = ["Easy", "Moderate", "Hard", "Extreme"]
DIFF_WEIGHTS = [25, 40, 25, 10]


def make_name(used):
    while True:
        name = f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)}"
        if name not in used:
            used.add(name)
            return name


def weighted(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def gen_row(used):
    difficulty = weighted(DIFFICULTIES, DIFF_WEIGHTS)
    state = weighted(STATES, STATE_WEIGHTS)
    trail_type = random.choice(TRAIL_TYPES)

    lo, hi = LENGTH_BY_DIFF[difficulty]
    length = round(random.uniform(lo, hi), 1)

    elo, ehi = ELEV_BY_DIFF[difficulty]
    # longer trails tend to climb more
    elev = int(random.uniform(elo, ehi) * (0.6 + length / hi))
    elev = max(elo, min(elev, ehi + 800))

    veh_opts, veh_w = VEHICLE_BY_DIFF[difficulty]
    vehicle = weighted(veh_opts, veh_w)

    # Rating: 1.0-5.0, gently centered ~4.0, slight bonus for scenic
    base = random.gauss(4.0, 0.5)
    if trail_type == "Scenic":
        base += 0.2
    rating = round(max(2.5, min(5.0, base)), 1)

    # Scenic score 1-100, higher for scenic/mountain, mild link to rating
    scenic_base = {
        "Scenic": 80, "Mountain": 72, "Forest": 65,
        "Desert": 62, "Rock Crawling": 55, "Mud": 50,
    }[trail_type]
    scenic = int(max(20, min(100, random.gauss(scenic_base, 12) + (rating - 4.0) * 5)))

    # Duration: scales with length and difficulty (slower = harder)
    speed = {"Easy": 9.0, "Moderate": 5.5, "Hard": 3.0, "Extreme": 1.5}[difficulty]
    duration = round(max(0.5, length / speed + random.uniform(0.2, 1.5)), 1)

    return {
        "Trail_Name": make_name(used),
        "State": state,
        "Difficulty": difficulty,
        "Length_Miles": length,
        "Elevation_Gain": elev,
        "Vehicle_Requirement": vehicle,
        "Rating": rating,
        "Trail_Type": trail_type,
        "Estimated_Duration_Hours": duration,
        "Scenic_Score": scenic,
    }


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "trails.csv")

    fields = [
        "Trail_Name", "State", "Difficulty", "Length_Miles", "Elevation_Gain",
        "Vehicle_Requirement", "Rating", "Trail_Type",
        "Estimated_Duration_Hours", "Scenic_Score",
    ]

    used = set()
    rows = [gen_row(used) for _ in range(200)]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} trails to {out_path}")


if __name__ == "__main__":
    main()
