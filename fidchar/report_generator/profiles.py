from models import ReportTable

def get_charity_profiles() -> list[dict]:
    return [
        {
            "name": "47 PALMER INC",
            "tax_id": "04-3255365",
            "sector": "Arts and Culture",
            "total_donations": "$228,600.00",
            "num_donations": 28,
            "evaluation": {"Outstanding": 4, "Acceptable": 6, "Unacceptable": 4},
            "alignment": 60,
            "notes": [
                "Focused on arts and humanities",
                "Spends just 3.7% on fundraising",
                "4-star Charity Navigator rating",
                "Operating for 20 years",
                "Based in Massachusetts",
                "High spending on salaries (63.82% on programs)",
                "Shows moderate alignment with user goals and mixed financial precision"
            ]
        },
        {
            "name": "Jewish Reconstructionist Federation",
            "tax_id": "13-2500888",
            "sector": "Religion",
            "total_donations": "$228,600.00",
            "num_donations": 19,
            "evaluation": {"Outstanding": 1, "Acceptable": 5, "Unacceptable": 8},
            "alignment": 0,
            "notes": [
                "Operating for 40 years",
                "Shows strong ethical compliance failures",
                "No recent Form 990 filing",
                "Financial history and expense details are missing"
            ]
        }
    ]