from collections import namedtuple
import logging

from snek.exts.syncer.syncers.base import Diff, ObjectSyncerABC

log = logging.getLogger(__name__)

Role = namedtuple('Role', ('id', 'name', 'color', 'permissions', 'position', 'guild'))


class RoleSyncer(ObjectSyncerABC):
    """Synchronise the database with roles in the cache."""
    name = 'role'

    async def get_diff(self) -> Diff:
        """Return the difference between the cache of roles and the database."""
        log.trace('Getting the diff for roles..')
        roles = await self.bot.api_client.get('roles/')

        db_roles = {Role(**role) for role in roles}
        cache_roles = {
            Role(
                id=role.id,
                name=role.name,
                color=role.color.value,
                permissions=role.permissions.value,
                position=role.position,
                guild=guild.id
            )
            for guild in self.bot.guilds
            for role in guild.roles
        }

        db_role_ids = {role.id for role in db_roles}
        cache_role_ids = {role.id for role in cache_roles}

        new_role_ids = cache_role_ids - db_role_ids
        deleted_role_ids = db_role_ids - cache_role_ids

        roles_to_create = {role for role in cache_roles if role.id in new_role_ids}
        roles_to_update = cache_roles - db_roles - roles_to_create
        roles_to_delete = {role for role in db_roles if role.id in deleted_role_ids}

        return Diff(roles_to_create, roles_to_update, roles_to_delete)

    async def sync_diff(self, diff: Diff) -> None:
        """Synchronise the database with the roles in the cache."""
        log.trace('Syncing created roles..')
        for role in diff.created:
            await self.bot.api_client.post('roles/', json=role._asdict())

        log.trace('Syncing updated roles..')
        for role in diff.updated:
            await self.bot.api_client.put(f'roles/{role.id}', json=role._asdict())

        log.trace('Syncing deleted roles..')
        for role in diff.deleted:
            await self.bot.api_client.delete(f'roles/{role.id}')
