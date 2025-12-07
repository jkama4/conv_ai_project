from .utils import setup_datasets

TRAVELER_LR: float = 0.001
TRAVELER_NUM_TRAIN_EPOCHS: int = 3
TRAIN_DS, VALIDATION_DS, TEST_DS = setup_datasets()

ASSISTANT_LR: float = 0.001
ASSISTANT_NUM_TRAIN_EPOCHS: int = 3