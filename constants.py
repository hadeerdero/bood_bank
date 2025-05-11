# constants.py
BLOOD_TYPES = [
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]

URGENCY = (
        ('immediate', 'Immediate (<2 hours)'),
        ('urgent', 'Urgent (<24 hours)'),
        ('normal', 'Normal (48+ hours)')
    )

BLOOD_STORAGE_TYPES = [
    ('whole', 'Whole Blood'),
    ('rbc', 'Red Blood Cells'),
    ('plasma', 'Plasma'),
    ('platelets', 'Platelets')
]

# EXPIRATION_DAYS = {
#     'whole': 35,
#     'rbc': 42,
#     'plasma': 365,
#     'platelets': 5
# }