# Snek Bot
The ultimate utility bot.

# Roadmap
This is what's currently planned for Snek.

- [x] Management Extension
    - [x] Extension Manager Cog
        - [x] Load
        - [x] Reload
        - [x] Unload
        - [x] List

- [x] Syncer Extension
    - [x] Syncer Cog (Syncs data with the Snek API)
        - [x] Sync guilds command
        - [x] Sync roles command
        - [x] Sync users command
        - [x] Resync at bot startup
        - [x] Auto updates (Listen to events and update dynamically)

- [x] Information Extension/Cog
    - [x] User information
    - [x] Role information
    - [x] Guild information
    - [x] Bot information
        - [x] Uptime
        - [x] Lines of code
        - [x] Repository
    - [x] Site/API information
        - [x] Homepage
        - [ ] Dashboard
        - [x] Repository

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

- [ ] Bookmark Extension/Cog
    - Takes a message ID and DMs it to the invoker

- [ ] Tags Extension/Cog (Each user has their own tags per guild)
    - [ ] Set
    - [ ] Get
    - [ ] Delete

- [x] Fun Extension/Cog
    - [x] Uwu
    - [x] Random case
    - [x] 8ball
    - [x] Flip a coin
    - [x] Roll a die

- [ ] Source Extension/Cog
    - Sends the link to the source of a command/cog (Use the inspect module)

- [ ] DEFCON Extension

    - [ ] Verification Cog
        - [ ] Level 1: No users able to verify
        - [ ] Level 2: Image captcha
        - [ ] Level 3: Text captcha
        - [ ] Level 4: Join command
        - [ ] Level 5: None

    - [ ] Lockdown Cog
        - [ ] Level 1: Server-wide lockdown, only mods+ can speak
        - [ ] Level 2: None
        - [ ] Level 3: None
        - [ ] Level 4: None
        - [ ] Level 5: None

- [ ] Remote Control Extension/Cog
    - Control the bot from a web dashboard
    - Establishes a websocket connection to the site
    - Execute commands, see guild statistics, check user info, etc. from the dashboard
