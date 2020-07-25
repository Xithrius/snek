# Snek Bot
The ultimate utility bot.

# Roadmap
This here is what's currently planned for Snek.

- [ ] Management Extension
    - [ ] Extension Manager Cog
        - [ ] Load
        - [ ] Reload
        - [ ] Unload
        - [ ] List

- [ ] Syncer Extension
    - [ ] Syncer Cog (Syncs data with the Snek API)
        - [ ] Sync guilds command
        - [ ] Sync roles command
        - [ ] Sync users command
        - [ ] Resync at bot startup
        - [ ] Auto updates (Listen to events and update dynamically)

- [ ] Information Extension/Cog
    - [ ] User information
    - [ ] Role information
    - [ ] Guild information
    - [ ] Bot/API source code

- [ ] Moderation Extension

    - [ ] Infractions Cog
        - [ ] Ban
        - [ ] Unban
        - [ ] Mute
        - [ ] Unmute
        - [ ] Kick
        - [ ] Temporary ban
        - [ ] Temporary mute
        - [ ] Watchdog
        - [ ] Force nick
        - [ ] Multi-ban
        - [ ] Multi-mute
        - [ ] Multi-kick

    - [ ] Silence Cog
        - [ ] Silence
        - [ ] Unsilence

    - [ ] Slowmode Cog
        - [ ] Get
        - [ ] Set
        - [ ] Reset

    - [ ] Filters Cog
        - [ ] Offensive language
        - [ ] Offensive username/nickname
        - [ ] Domain blacklist
        - [ ] Discord invite links
            - If guild members > `x` members: allow; else: disallow
            - Whitelist to allow & bypass check
            - Blacklist to disallow & bypass check
        - [ ] Embeds

    - [ ] Antispam
        - [ ] Burst
        - [ ] Discord Emojis
        - [ ] Duplicates
        - [ ] Characters
        - [ ] Mentions
        - [ ] Newlines

    - [ ] Purge Cog
        - [ ] Bot messages only
        - [ ] A specific user's messages only
        - [ ] Messages from anyone
        - [ ] Regex matching
        - [ ] Up until a specific message

- [ ] Logging Extension/Cog
    - [ ] Message changes/deletions
    - [ ] User joins/changes/leaves
    - [ ] Moderator actions
    - [ ] Watchdog
    - [ ] Attachments

- [ ] Reminders Extension/Cog (Each user has their own reminders per guild)
    - [ ] Create
    - [ ] Edit
    - [ ] Delete
    - [ ] List

- [ ] Tags Extension/Cog (Each user has their own tags per guild)
    - [ ] Set
    - [ ] Get
    - [ ] Delete

- [ ] DEFCON Extension

    - [ ] Verification Cog
        - [ ] Level 1: No users able to verify
        - [ ] Level 2: Image captcha
        - [ ] Level 3: Text captcha
        - [ ] Level 4: Join command
        - [ ] Level 5: None

    - [ ] Lockdown Cog
        - [ ] Level 1: Server-wide lockdown, only mods+ can speak

- [ ] Remote Control Cog
    - Control the bot from a web dashboard
    - Establishes a websocket connection to the site
    - Execute commands, see guild statistics, check user info, etc. from the dashboard
