import hashlib
from pathlib import Path


DATASET = Path("data/generated/synthetic_data.csv")
HASH_FILE = Path("data_integrity/synthetic_data.sha256")


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_baseline_hash():
    current_hash = calculate_sha256(DATASET)

    HASH_FILE.write_text(
        current_hash,
        encoding="utf-8"
    )

    print("Baseline dataset hash created.")
    print(f"SHA-256: {current_hash}")


def verify_dataset_integrity():

    if not DATASET.exists():
        print("INTEGRITY CHECK FAILED")
        print("Dataset file does not exist.")
        return False

    if not HASH_FILE.exists():
        print("INTEGRITY CHECK FAILED")
        print("Trusted baseline hash does not exist.")
        return False

    expected_hash = HASH_FILE.read_text(
        encoding="utf-8"
    ).strip()

    actual_hash = calculate_sha256(DATASET)

    if actual_hash != expected_hash:
        print("INTEGRITY CHECK FAILED")
        print("Dataset hash does not match the trusted baseline.")
        print(f"Expected: {expected_hash}")
        print(f"Actual:   {actual_hash}")
        return False

    print("DATASET INTEGRITY VERIFIED")
    print(f"SHA-256: {actual_hash}")

    return True


if __name__ == "__main__":
    verify_dataset_integrity()