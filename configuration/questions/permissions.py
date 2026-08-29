from django.core.exceptions import PermissionDenied

def can_manage_questions(user):
    return user.is_authenticated and (user.is_staff or user.has_perm("questions.change_question"))

def can_publish_questions(user):
    return user.is_authenticated and (user.is_staff or user.has_perm("questions.publish_question"))

def ensure_submission_access(user, submission):
    if not user.is_authenticated or (submission.user_id != user.pk and not user.is_staff):
        raise PermissionDenied
