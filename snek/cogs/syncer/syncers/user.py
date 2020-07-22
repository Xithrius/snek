from collections import namedtuple
import logging

from snek.cogs.syncer.syncers.base import Diff, ObjectSyncerABC

log = logging.getLogger(__name__)

User = namedtuple('User', ('id', 'name', 'discriminator', 'avatar_url', 'roles', 'guilds'))


class UserSyncer(ObjectSyncerABC):
    """Synchronise the database with users in the cache."""
    name = 'user'

    async def get_diff(self) -> Diff:
        """Return the difference between the cache of users and the database."""
        log.trace('Getting diff for users..')
        users = await self.bot.api_client.get('users/')

        db_users = {
            User(
                guilds=tuple(user.pop('guilds')),
                roles=tuple(user.pop('roles')),
                **user
            )
            for user in users
        }
        db_user_ids = {user.id for user in db_users}

        cache_users_dict = dict()
        for guild in self.bot.guilds:
            for user in guild.members:
                if user.id in cache_users_dict.keys():
                    user_dict = cache_users_dict[user.id]._asdict()
                    roles = user_dict.pop('roles') + tuple(role.id for role in user.roles)
                    cache_users_dict[user.id] = User(
                        roles=tuple(sorted(roles)),
                        **user_dict
                    )

                else:
                    cache_users_dict[user.id] = User(
                        id=user.id,
                        name=user.name,
                        discriminator=user.discriminator,
                        avatar_url=str(user.avatar_url),
                        roles=tuple(sorted(role.id for role in user.roles)),
                        guilds=tuple(g.id for g in self.bot.guilds if g.get_member(user.id) is not None)
                    )

        cache_users = set(cache_users_dict.values())
        cache_user_ids = set(cache_users_dict.keys())

        new_user_ids = cache_user_ids - db_user_ids

        users_to_create = {user for user in cache_users if user.id in new_user_ids}
        users_to_update = cache_users - db_users - users_to_create

        return Diff(users_to_create, users_to_update, None)

    async def sync_diff(self, diff: Diff) -> None:
        """Synchronise the database with the users in the cache."""
        log.trace('Syncing created users..')
        for user in diff.created:
            await self.bot.api_client.post('users/', json=user._asdict())

        log.trace('Syncing updated users..')
        for user in diff.updated:
            await self.bot.api_client.put(f'users/{user.id}', json=user._asdict())
