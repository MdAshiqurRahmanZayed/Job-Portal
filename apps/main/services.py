import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Application, Job, Notification

logger = logging.getLogger(__name__)


def _broadcast(group_name, event):
    """Best-effort push. A broadcast failure (e.g. Redis unreachable)
    must never break the underlying write it's attached to - real-time
    push is an enhancement on top of the HTTP write path, not a
    dependency of it."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(group_name, event)
    except Exception:
        logger.exception(
            "Failed to broadcast %s to group %s", event.get("type"), group_name
        )


def create_job(employer_profile, form):
    job = form.save(commit=False)
    job.user = employer_profile
    job.save()
    return job


def update_job(job, form):
    job = form.save(commit=False)
    job.save()
    return job


def delete_job(job: Job) -> None:
    job.delete()


def create_notification(
    to_user, notification_type, created_by, application, extra_id=0
):
    notification = Notification.objects.create(
        to_user=to_user,
        notification_type=notification_type,
        created_by=created_by,
        extra_id=extra_id,
        application=application,
    )

    _broadcast(
        f"notifications_{to_user.id}",
        {
            "type": "notification.new",
            "payload": {
                "id": notification.id,
                "notification_type": notification.notification_type,
                "extra_id": notification.extra_id,
                "created_at": notification.created_at.isoformat(),
            },
        },
    )

    return notification


def submit_application(applicant_profile, job, form):
    application = form.save(commit=False)
    application.job = job
    application.user = applicant_profile
    application.save()
    create_notification(
        to_user=job.user,
        notification_type="application",
        created_by=applicant_profile,
        application=application,
        extra_id=application.id,
    )
    return application


def post_conversation_message(actor_profile, application, form):
    message = form.save(commit=False)
    message.created_by = actor_profile
    message.application = application
    message.save()

    _broadcast(
        f"chat_{application.id}",
        {
            "type": "chat.message",
            "payload": {
                "id": message.id,
                "content": message.content,
                "created_by_id": actor_profile.id,
                "created_by_name": actor_profile.get_full_name(),
                "created_at": message.created_at.isoformat(),
            },
        },
    )

    if actor_profile.role == "employer":
        notify_user = application.user
    else:
        notify_user = application.job.user

    create_notification(
        to_user=notify_user,
        notification_type="message",
        created_by=actor_profile,
        application=application,
        extra_id=application.id,
    )
    return message


def delete_application(application: Application) -> None:
    application.delete()
