STEP_TENNIS = "tennis"
STEP_SHOT = "shot"


class StepService:
    _current_step = STEP_TENNIS

    def __init__(self):
        pass

    def step_change(self):
        if self._current_step == STEP_SHOT:
            self._current_step = STEP_TENNIS
        else:
            self._current_step = STEP_SHOT

    def current_step(self):
        return self._current_step
