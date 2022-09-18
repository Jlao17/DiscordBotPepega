from helpers import db_manager
from db_manager import startsql as sql

async def is_blacklisted(user_id: int) -> bool:
    """
    This function will check if a user is blacklisted.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is blacklisted, False if not.
    """
    result = await sql.execute("SELECT * FROM blacklist WHERE user_id=?", (user_id,))
    return result is not None


async def add_user_to_blacklist(user_id: int) -> int:
    """
    This function will add a user based on its ID in the blacklist.

    :param user_id: The ID of the user that should be added into the blacklist.
    """
    await sql.execute("INSERT INTO blacklist(user_id) VALUES (?)", (user_id,))
    rows = await sql.fetchone("SELECT COUNT(*) FROM blacklist")
    return rows[0]


async def remove_user_from_blacklist(user_id: int) -> int:
    """
    This function will remove a user based on its ID from the blacklist.

    :param user_id: The ID of the user that should be removed from the blacklist.
    """
    await sql.execute("DELETE FROM blacklist WHERE user_id=?", (user_id,))
    rows = await sql.fetchone("SELECT COUNT(*) FROM blacklist")
    return rows[0]


async def add_warn(user_id: int, server_id: int, moderator_id: int, reason: str) -> int:
    """
    This function will add a warn to the database.

    :param user_id: The ID of the user that should be warned.
    :param reason: The reason why the user should be warned.
    """
    # Get the last `id`
    rows = await sql.fetchone("SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1",
                          (user_id, server_id,))
    warn_id = rows[0] + 1 if rows is not None else 1
    await sql.execute("INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)",
                   (warn_id, user_id, server_id, moderator_id, reason,))
    rows = await sql.fetchone("SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?", (user_id, server_id,))
    return rows[0]


async def remove_warn(warn_id: int, user_id: int, server_id: int) -> int:
    """
    This function will remove a warn from the database.

    :param warn_id: The ID of the warn.
    :param user_id: The ID of the user that was warned.
    :param server_id: The ID of the server where the user has been warned
    """
    await sql.execute("DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?", (warn_id, user_id, server_id,))
    rows = await sql.fetchone("SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?", (user_id, server_id,))
    return rows[0]


async def get_warnings(user_id: int, server_id: int) -> list:
    """
    This function will get all the warnings of a user.

    :param user_id: The ID of the user that should be checked.
    :param server_id: The ID of the server that should be checked.
    :return: A list of all the warnings of the user.
    """
    result = await sql.fetchall("SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id FROM warns WHERE user_id=? AND server_id=?",
        (user_id, server_id,))
    return result
