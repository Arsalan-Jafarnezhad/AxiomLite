class QuestionsError(Exception):
    pass
class ExecutionError(QuestionsError):
    pass
class UnsupportedEvaluator(QuestionsError):
    pass
