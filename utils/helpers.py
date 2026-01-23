import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from guardian.shortcuts import assign_perm

logger = logging.getLogger(__name__)
User = get_user_model()


# utils/helpers.py or core/utils.py
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def assign_object_to_group(obj, *args, **kwargs):
    groups = kwargs["kwargs"].keys()
    for group in groups:
        group_obj, _ = Group.objects.get_or_create(name=group)
        for permission in kwargs["kwargs"][group]:
            try:
                assign_perm(perm=permission, user_or_group=group_obj, obj=obj)
                logger.info(f"assigned {obj} {permission} to {group}")
            except Exception as e:
                logger.error(f"An error occurred {e}")
                raise e


def assign_object_to_user(obj, permissions, user):
    for permission in permissions:
        try:
            assign_perm(perm=permission, user_or_group=user, obj=obj)
            logger.info(f"assigned {obj} {permission} to {user.username}")
        except Exception as e:
            logger.error(f"An error occurred {e}")


class BaseTest(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create(
            username="testuser", email="testuser@mail.com", password="testuser123"
        )
        self.pastor = User.objects.create(
            username="pastor", email="pastor@mail.com", password="testuser123"
        )

        self.admin_group = Group.objects.create(name="admin")
        self.pastor_group = Group.objects.create(name="pastor")

        self.admin.groups.add(self.admin_group)
        self.pastor.groups.add(self.pastor_group)
