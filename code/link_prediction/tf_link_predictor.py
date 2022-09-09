from path import Path
from .link_predictor import LinkPredictor
from .models.link_prediction import load_saved_model, params

class TensorflowLinkPredictor(LinkPredictor):
    """
    Uses the trained model to perform the prediction task
    """
    
    def __init__(self, model_path: Path, max_worker: int, max_argumentative_distance: int) -> None:
        super().__init__(max_worker=max_worker, max_argumentative_distance=max_argumentative_distance)
        self.model = None
        self._load_model(model_path)

    def _load_model(self, model_path: Path):
        """
        Load the tensorflow model from disk
        """
        pass
    
    def links_from_arguments(self, source_argument: str, target_argument: str, distance: int) -> Tuple[str, str, str]:
        pass