import time
from ghostscript import convert_to_pdfa


def measure_conversion_time(function) -> float:
    """Measure the time taken to convert PDF to PDF/A-2 format."""
    start_time = time.time()
    function
    end_time = time.time()
    return end_time - start_time

