from ..data.charity_evaluation_result import ExternalValidation


class ValidationScorer:
    def __init__(self, config: dict):
        self.config = config
    
    def get_validation_data(self, ein: str) -> ExternalValidation:
        return ExternalValidation(
            charity_navigator_rating=4,
            charity_navigator_score=20.0,
            has_transparency_seal=True,
            has_advisory_alerts=False,
            negative_news_alerts=0
        )
    
    def calculate_bonus(self, validation: ExternalValidation) -> float:
        return validation.charity_navigator_score