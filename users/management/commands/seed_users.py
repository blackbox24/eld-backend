from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from utils.helpers import assign_object_to_group

User = get_user_model()

GROUP_PERMISSIONS = {
    "customuser": {
        "view": ["driver", "admin"],
        "add": ["driver", "admin"],
        "change": ["driver", "admin"],
        "delete": ["admin"],
    },
    "trip": {
        "view": ["driver", "admin"],
        "add": [
            "driver",
        ],
    },
}


class Command(BaseCommand):
    help = "Setup: Groups, Permissions, Superuser & Sample Data"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--skip-users",
            action="store_true",
            help="Skip creating test users (useful in production)",
        )

    # create users

    def handle(self, *args, **options):
        self.stdout.write("Starting initial setup...")

        with transaction.atomic():
            # 1. Create Groups
            groups = self.create_groups()

            # 2. Assign Model Permissions
            self.assign_model_permissions(groups)

            # 3. Create Superuser & Test Users (skip in prod if needed)
            if not options["skip_users"]:
                self.create_customusers(groups)

        self.stdout.write(self.style.SUCCESS("Initial setup completed successfully!"))

    def create_groups(self):
        group_names = ["driver", "admin"]
        groups = {}
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            status = "created" if created else "already exists"
            self.stdout.write(f"Group '{name}' {status}")
            groups[name] = group
        return groups

    def assign_model_permissions(self, groups) -> None:
        for model_name, actions in GROUP_PERMISSIONS.items():
            app_label = self.get_app_label(model_name)
            print(app_label, model_name)
            for action, group_list in actions.items():
                codename = f"{action}_{model_name}"
                try:
                    perm = Permission.objects.get(
                        codename=codename, content_type__app_label=app_label
                    )
                    for group_name in group_list:
                        if group_name in groups:
                            groups[group_name].permissions.add(perm)
                            self.stdout.write(self.style.SUCCESS(f"✓ {codename} → {group_name}"))
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Permission {app_label}.{codename} does not exist!")
                    )

    def get_app_label(self, model_name):
        mapping = {
            "customuser": "users",
            "trip": "trip",
        }
        return mapping.get(model_name, "users")

    def create_customusers(self, groups):
        users_data: list[dict] = [
            {
                "username": "superadmin",
                "email": "nelsondecardikwame24th@gmail.com",
                "password": "admin123",
                "group": "admin",
                "staff": True,
                "super": True,
            },
            {
                "username": "admin",
                "email": "nelsondecardikwame24th+1@gmail.com",
                "password": "admin123",
                "group": "admin",
            },
            {
                "username": "driver",
                "email": "nelsondecardikwame24th+2@gmail.com",
                "password": "driver123",
                "group": "driver",
            },
            {
                "username": "driver1",
                "email": "pastor@school.com",
                "password": "driver123",
                "group": "driver",
            },
        ]

        for data in users_data:
            if User.objects.filter(username=data["username"]).exists():
                self.stdout.write(self.style.WARNING(f"User {data['username']} exists"))
                continue

            user = User.objects.create_user(  # pyright: ignore[reportAttributeAccessIssue]
                username=data["username"],
                email=data["email"],
                password=data["password"],
                is_staff=data.get("staff", True),
                is_superuser=data.get("super", False),
            )
            user.groups.add(groups[data["group"]])
            self.stdout.write(self.style.SUCCESS(f"Created {data['username']} → {data['group']}"))

            assign_object_to_group(
                obj=user,
                kwargs={
                    "driver": [
                        "users.view_customuser",
                    ],
                    "admin": [
                        "users.view_customuser",
                        "users.change_customuser",
                    ],
                },
            )
