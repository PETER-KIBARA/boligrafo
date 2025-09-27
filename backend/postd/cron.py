from .tasks import check_missing_vitals, check_missed_prescriptions

def run_checks():
    check_missing_vitals()
    check_missed_prescriptions()
