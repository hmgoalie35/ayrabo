"""
Not needed as of now, django all auth will create EmailAddress & EmailConfirmation
object next time user logs in if user was created
via admin panel or via User.objects.create

@receiver(post_save, sender=User)
def create_necessary_all_auth_models(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    email = instance.email
    if email is None or email.strip() == '':
        email = instance.username
    if created:
        EmailAddress.objects.add_email(None, instance, email)
"""
