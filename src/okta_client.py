"""
okta_client.py

Responsible for connecting to the Okta API and pulling all the user data
we need for the access review. Think of this as the "data collection" layer —
it doesn't analyze anything, it just fetches and organizes raw information.
"""

import asyncio
import os
from dotenv import load_dotenv
from okta.client import Client as OktaClient


# Load environment variables from the .env file into os.environ
load_dotenv()


def build_okta_client() -> OktaClient:
    """
    Creates and returns an authenticated Okta API client.

    The Okta SDK expects a config dictionary with your org URL and API token.
    We pull both from environment variables so they never live in the code.

    Returns:
        OktaClient: A ready-to-use Okta client instance.
    """
    config = {
        "orgUrl": f"https://{os.environ['OKTA_DOMAIN']}",
        "token": os.environ["OKTA_API_TOKEN"],
    }
    return OktaClient(config)


async def get_all_users(client: OktaClient) -> list[dict]:
    """
    Fetches every active user in the Okta org and returns the fields
    we care about for an access review.

    Okta returns users in pages (default 200 per page). The SDK handles
    pagination automatically when we loop using resp.next() — we keep
    fetching until there are no more pages.

    Args:
        client: An authenticated OktaClient instance.

    Returns:
        A list of dicts, one per user, with these keys:
            - id             (str)       Okta's internal user ID — used to look up apps/groups
            - login          (str)       The user's email/username
            - first_name     (str)       First name
            - last_name      (str)       Last name
            - status         (str)       e.g. "ACTIVE", "SUSPENDED", "DEPROVISIONED"
            - last_login     (str|None)  ISO timestamp or None if they've never logged in
            - created        (str|None)  ISO timestamp when the account was created
            - department     (str|None)  Department name
            - title          (str|None)  Job title
            - user_type      (str|None)  Employee type (full_time, contractor, service_account)
            - manager        (str|None)  Manager's login/email
            - mobile_phone   (str|None)  Mobile phone number
            - city           (str|None)  City
            - state          (str|None)  State/province
            - cost_center    (str|None)  Cost center code
            - employee_number(str|None)  Employee ID
    """
    users = []

    query_params = {"limit": 200}
    user_list, resp, err = await client.list_users(query_params)

    if err:
        raise RuntimeError(f"Failed to fetch users from Okta: {err}")

    # Loop through every page of results
    while True:
        for user in user_list:
            profile = user.profile

            # last_login and created may come back as datetime or string
            # depending on the Okta SDK version — handle both
            last_login = user.last_login if user.last_login else None
            if last_login and hasattr(last_login, "isoformat"):
                last_login = last_login.isoformat()

            created = user.created if user.created else None
            if created and hasattr(created, "isoformat"):
                created = created.isoformat()

            # password_changed may be on the user object or credentials
            password_changed = getattr(user, "password_changed", None)
            if password_changed and hasattr(password_changed, "isoformat"):
                password_changed = password_changed.isoformat()

            users.append({
                "id": user.id,
                "login": profile.login,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "status": user.status.value,
                "last_login": last_login,
                "created": created,
                "password_changed": password_changed,
                "department": getattr(profile, "department", None),
                "title": getattr(profile, "title", None),
                "user_type": getattr(profile, "user_type", None),
                "manager": getattr(profile, "manager", None),
                "mobile_phone": getattr(profile, "mobile_phone", None),
                "city": getattr(profile, "city", None),
                "state": getattr(profile, "state", None),
                "cost_center": getattr(profile, "cost_center", None),
                "employee_number": getattr(profile, "employee_number", None),
            })

        # If there's another page, fetch it; otherwise stop
        if resp.has_next():
            user_list, err = await resp.next()
            if err:
                raise RuntimeError(f"Failed to fetch next page of users: {err}")
        else:
            break

    return users


async def get_user_app_assignments(client: OktaClient, user_id: str) -> list[str]:
    """
    Returns the names of all apps assigned to a specific user.

    In IAM, knowing what apps a user can access is core to spotting
    over-provisioning — e.g. a contractor still assigned to internal finance tools.

    Args:
        client:  An authenticated OktaClient instance.
        user_id: The Okta user ID (the 'id' field from get_all_users).

    Returns:
        A list of app label strings, e.g. ["Salesforce", "GitHub", "Workday"].
    """
    app_names = []

    app_links, resp, err = await client.list_app_links(user_id)

    if err:
        raise RuntimeError(f"Failed to fetch app assignments for user {user_id}: {err}")

    while True:
        for app in app_links:
            app_names.append(app.label)

        if resp.has_next():
            app_links, err = await resp.next()
            if err:
                raise RuntimeError(f"Failed to fetch next page of apps for user {user_id}: {err}")
        else:
            break

    return app_names


async def get_user_groups(client: OktaClient, user_id: str) -> list[str]:
    """
    Returns the names of all groups a user belongs to.

    Groups in Okta often map directly to access levels or departments.
    Seeing a user in unexpected groups (e.g. an intern in "Finance-Admins")
    is a classic over-provisioning red flag.

    Args:
        client:  An authenticated OktaClient instance.
        user_id: The Okta user ID.

    Returns:
        A list of group name strings, e.g. ["Everyone", "Engineering", "VPN-Users"].
    """
    group_names = []

    groups, resp, err = await client.list_user_groups(user_id)

    if err:
        raise RuntimeError(f"Failed to fetch groups for user {user_id}: {err}")

    while True:
        for group in groups:
            group_names.append(group.profile.name)

        if resp.has_next():
            groups, err = await resp.next()
            if err:
                raise RuntimeError(f"Failed to fetch next page of groups for user {user_id}: {err}")
        else:
            break

    return group_names


async def get_user_admin_roles(client: OktaClient, user_id: str) -> list[str]:
    """
    Returns any admin roles assigned directly to a user.

    Admin roles are high-privilege assignments in Okta — things like
    "SUPER_ADMIN", "ORG_ADMIN", or "APP_ADMIN". These should be tightly
    controlled and are a priority target for access reviews.

    Note: This only captures roles assigned *directly* to the user, not
    roles inherited through groups. Group-based roles would require a
    separate check.

    Args:
        client:  An authenticated OktaClient instance.
        user_id: The Okta user ID.

    Returns:
        A list of role type strings, e.g. ["SUPER_ADMIN"] or [] if none.
    """
    role_names = []

    roles, resp, err = await client.list_assigned_roles_for_user(user_id)

    if err:
        # A 403 here usually means the API token lacks admin role read permission
        raise RuntimeError(f"Failed to fetch admin roles for user {user_id}: {err}")

    while True:
        for role in roles:
            role_names.append(role.type.value)

        if resp.has_next():
            roles, err = await resp.next()
            if err:
                raise RuntimeError(f"Failed to fetch next page of roles for user {user_id}: {err}")
        else:
            break

    return role_names


async def collect_all_user_data(client: OktaClient) -> list[dict]:
    """
    The main function for this module. Pulls all users and then enriches
    each one with their app assignments, group memberships, and admin roles.

    This is the single function that main.py will call — it returns one
    complete, self-contained record per user ready to hand off to the analyzer.

    Args:
        client: An authenticated OktaClient instance.

    Returns:
        A list of fully enriched user dicts, each with keys:
            id, login, first_name, last_name, status, last_login, created,
            password_changed, department, title, user_type, manager,
            mobile_phone, city, state, cost_center, employee_number,
            apps, groups, admin_roles, risk_signals
    """
    print("Fetching users from Okta...")
    users = await get_all_users(client)
    print(f"Found {len(users)} users. Fetching access details...")

    # For each user, fetch their apps, groups, and roles in parallel.
    # asyncio.gather() runs multiple async calls at the same time instead of
    # waiting for each one to finish before starting the next — much faster.
    for i, user in enumerate(users):
        user_id = user["id"]

        apps, groups, admin_roles = await asyncio.gather(
            get_user_app_assignments(client, user_id),
            get_user_groups(client, user_id),
            get_user_admin_roles(client, user_id),
        )

        user["apps"] = apps
        user["groups"] = groups
        user["admin_roles"] = admin_roles

        # Simple progress indicator so we know it's working
        print(f"  [{i + 1}/{len(users)}] Collected data for {user['login']}")

    # Pre-compute risk signals that are easier to calculate here than
    # ask the AI to derive from raw data
    print("Computing risk signals...")
    _compute_risk_signals(users)

    print("Done collecting Okta data.")
    return users


def _compute_risk_signals(users: list[dict]) -> None:
    """
    Pre-computes risk signals from the collected data and attaches them
    to each user dict. These give the AI concrete flags to work with
    instead of asking it to derive everything from raw fields.

    Signals computed:
      - is_contractor:        True if user_type contains "contractor"
      - is_service_account:   True if login starts with "svc."
      - has_no_manager:       True if manager field is empty
      - profile_incomplete:   True if key profile fields are missing
      - app_count:            Total number of app assignments
      - group_count:          Total number of group memberships
      - department_groups:    List of department groups (dept-*) the user is in
      - cross_dept_count:     Number of department groups beyond their own
      - possible_duplicates:  Logins of other users with the same first+last name

    Args:
        users: The enriched user list — modified in place.
    """
    # Build a name→logins index to detect duplicate identities
    name_index: dict[str, list[str]] = {}
    for user in users:
        full_name = f"{user['first_name']} {user['last_name']}".strip().lower()
        if full_name:
            name_index.setdefault(full_name, []).append(user["login"])

    for user in users:
        login = user["login"]
        user_type = (user.get("user_type") or "").lower()
        department = (user.get("department") or "").lower()

        # Identity flags
        is_contractor = "contractor" in user_type
        is_service_account = login.startswith("svc.") or "service" in user_type

        # Manager and profile completeness
        has_no_manager = not user.get("manager")
        missing_fields = [
            f for f in ["mobile_phone", "city", "state", "cost_center"]
            if not user.get(f)
        ]
        profile_incomplete = len(missing_fields) >= 2

        # Access volume
        app_count = len(user.get("apps", []))
        group_count = len(user.get("groups", []))

        # Cross-department group analysis
        dept_groups = [
            g for g in user.get("groups", [])
            if "dept-" in g.lower() and "everyone" not in g.lower()
        ]
        # The user's own dept group is expected — anything beyond that is cross-dept
        own_dept_group = f"dept-{department}" if department else ""
        cross_dept = [g for g in dept_groups if own_dept_group not in g.lower()]

        # Duplicate identity detection
        full_name = f"{user['first_name']} {user['last_name']}".strip().lower()
        name_matches = name_index.get(full_name, [])
        possible_dupes = [l for l in name_matches if l != login]

        user["risk_signals"] = {
            "is_contractor": is_contractor,
            "is_service_account": is_service_account,
            "has_no_manager": has_no_manager,
            "profile_incomplete": profile_incomplete,
            "missing_profile_fields": missing_fields,
            "app_count": app_count,
            "group_count": group_count,
            "department_groups": dept_groups,
            "cross_dept_count": len(cross_dept),
            "possible_duplicates": possible_dupes,
        }
