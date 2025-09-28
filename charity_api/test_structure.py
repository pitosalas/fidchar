from api.charity_evaluator import evaluate_charity


def test_package_interface():
    result = evaluate_charity("530196605", "config/test_config.yaml")
    
    print(f"Organization: {result.organization_name}")
    print(f"EIN: {result.ein}")
    print(f"Total Score: {result.total_score}")
    print(f"Grade: {result.grade}")
    print(f"Financial Score: {result.financial_score}")
    print(f"Trend Modifier: {result.trend_modifier}")
    print(f"Validation Bonus: {result.validation_bonus}")
    print(f"Compliance Penalty: {result.compliance_penalty}")
    print("Structure test passed!")


if __name__ == "__main__":
    test_package_interface()