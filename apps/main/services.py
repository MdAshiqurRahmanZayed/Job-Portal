from .models import Application, Job, Notification


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
    return Notification.objects.create(
        to_user=to_user,
        notification_type=notification_type,
        created_by=created_by,
        extra_id=extra_id,
        application=application,
    )


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
