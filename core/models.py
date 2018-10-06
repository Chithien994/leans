from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.dispatch.dispatcher import receiver
from rest_framework.authtoken.models import Token


def get_file_path(instance, filename):
    """
    :param instance:
    :param filename:
    :return:
    """
    ext = filename.split('.')[-1]
    now = datetime.datetime.now()
    filename = '%s.%s' % (str(hashlib.sha224(str(filename) +
                                             str(now.microsecond)).hexdigest()), ext)
    return os.path.join(instance.directory_string_var, filename)


def photo_upload_to(instance, filename):
    return os.path.join(instance.directory_string_var, str(instance.id), '%s_profile_picture.jpg'%(instance.phone_number))

def get_thumbnail_path(instance, filename):
    """
    :param instance:
    :param filename:
    :return:
    """
    ext = filename.split('.')[-1]
    now = datetime.datetime.now()
    filename = '%s/%s-%s.%s' % (now.strftime('%Y/%m/%d'),
                                filename.replace('.' + ext, ''), str(now.microsecond), ext)
    return os.path.join(instance.directory_string_var, filename)

@python_2_unicode_compatible
class DateTimeModel(models.Model):
    """
    Abstract model that is used for the model using created and modified fields
    """
    created = models.DateTimeField(_('Created'), auto_now_add=True, editable=False)
    modified = models.DateTimeField(_('Modified'), auto_now=True, editable=False)

    def __init__(self, *args, **kwargs):
        super(DateTimeModel, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class LeanUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone_number, password):
        """
        Creates and saves a superuser with the given email, phone_number and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class LeanUser(DateTimeModel, AbstractBaseUser):
    email = models.EmailField(max_length=80,unique=True)
    profile_picture = models.ImageField(upload_to=photo_upload_to, max_length=255, null=True, blank=True, default='default/avatar-default.jpg')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    address = models.CharField(null=True, blank=True, max_length=300, default='')
    objects = LeanUserManager()
    directory_string_var = ''

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'first_name']

    def __str__(self):
        return '%s' % (self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_perms(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def delete(self, *args, **kwargs):
        try:
            if 'default' not in str(self.profile_picture):
                self.profile_picture.delete()
        except:
            pass
        super(LeanUser, self).delete(*args, **kwargs)


    class Meta:
        db_table = 'users'
        verbose_name_plural = 'Lean Users'


@receiver(models.signals.post_save, sender=LeanUser)
def create_token(sender, instance, created, **kwargs):
    if created:
        try:
            token, created = Token.objects.get_or_create(user=instance)
        except:
            pass


@receiver(models.signals.pre_save, sender=LeanUser)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
        Deletes file from filesystem
    """
    if not instance.pk:
        return False
    try:
        old_profile_picture = LeanUser.objects.get(pk=instance.pk).profile_picture
    except LeanUser.DoesNotExist:
        return False
    new_profile_picture = instance.profile_picture
    if not old_profile_picture == new_profile_picture and 'default' not in str(instance.profile_picture):
        try:
            old_profile_picture.delete(save=False)
        except:
            pass