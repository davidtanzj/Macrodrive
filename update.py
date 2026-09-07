import subprocess
import sys
import time
from datetime import datetime


PIPELINE = [
    (
        "Collecting articles",
        "collector.py"
    ),
    (
        "Processing article text",
        "textprocessor.py"
    ),
    (
        "Classifying macro relevance and topics",
        "processor.py"
    ),
    (
        "Detecting regions",
        "regionprocessor.py"
    ),
    (
        "Updating US macro calendar schedule",
        "calendarcollector.py"
    ),
    (
        "Updating released macro values",
        "calendarvalues.py"
    ),
]


def run_step(
    step_number,
    total_steps,
    description,
    filename
):
    print()
    print("=" * 72)
    print(
        f"STEP {step_number}/{total_steps}"
    )
    print(
        description.upper()
    )
    print("=" * 72)
    print()

    start_time = time.time()

    result = subprocess.run(
        [
            sys.executable,
            "-u",
            filename
        ]
    )

    elapsed = (
        time.time()
        - start_time
    )

    if result.returncode != 0:
        print()
        print("=" * 72)
        print(
            "Macrodrive UPDATE FAILED"
        )
        print("=" * 72)
        print(
            f"Failed step: "
            f"{description}"
        )
        print(
            f"File: "
            f"{filename}"
        )
        print(
            f"Exit code: "
            f"{result.returncode}"
        )
        print()
        print(
            "The remaining steps were "
            "not run."
        )
        print("=" * 72)

        return False

    print()
    print(
        f"Completed in "
        f"{elapsed:.1f} seconds."
    )

    return True


def run_update():
    print()
    print("=" * 72)
    print(
        "Macrodrive UPDATE"
    )
    print("=" * 72)
    print(
        "Started: "
        + datetime.now().strftime(
            "%d %b %Y %H:%M:%S"
        )
    )
    print("=" * 72)

    total_steps = len(
        PIPELINE
    )

    overall_start = (
        time.time()
    )

    for index, (
        description,
        filename
    ) in enumerate(
        PIPELINE,
        start=1
    ):
        success = run_step(
            index,
            total_steps,
            description,
            filename
        )

        if not success:
            return

    total_elapsed = (
        time.time()
        - overall_start
    )

    print()
    print("=" * 72)
    print(
        "Macrodrive UPDATE COMPLETE"
    )
    print("=" * 72)
    print(
        "Finished: "
        + datetime.now().strftime(
            "%d %b %Y %H:%M:%S"
        )
    )
    print(
        f"Total time: "
        f"{total_elapsed:.1f} seconds"
    )
    print()
    print(
        "The website database is now "
        "up to date."
    )
    print("=" * 72)


if __name__ == "__main__":
    run_update()
