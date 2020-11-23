"""
Set the SCHEMA_VERSION for your code

If you look in /bot/database you will notice a v0.sqlite.
You can upgrade the database with new tables/columns or
modify existing ones by creating a v1.sqlite, v2.sqlite,
ext.. The bot will run the SQLite scripts sequentially
to the version specified below. Note that once a
database is upgraded, it must be manually downgraded.

To learn more about migrating databases, see SQLite
ALTER and ADD commands, as they are the most useful
commands to use with migrations.

Also make sure your migration updates the meta table with
the right version, as shown in v0.sqlite.
"""
SCHEMA_VERSION = 2
