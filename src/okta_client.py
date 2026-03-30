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
            - id           (str)  Okta's internal user ID — used to look up apps/groups
            - login        (str)  The user's email/username
            - first_name   (str)
            - last_name    (str)
            - status       (str)  e.g. "ACTIVE", "SUSPENDED", "DEPROVISIONED"
            - last_login   (str)  ISO timestamp or None if they've never logged in
            - created      (str)  ISO timestamp when the account was created
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

            users.append({
                "id": user.id,
                "login": profile.login,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "status": user.status.value,
                "last_login": last_login,
                "created": created,
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
            id, login, first_name, last_name, status, last_login,
            created, apps, groups, admin_roles
    """
    print("Fetching users from Okta...")
    users = await get_all_users(client)
    print(f"Found {len(users)} active users. Fetching access details...")

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

    print("Done collecting Okta data.")
    return users
