"""Read-only tooling for the Curriculum Factory repository refactor (spec v8).

Everything under this package only reads the repository it is pointed at
(via git, the filesystem, and Python's ``ast`` module) and writes only to a
caller-supplied output directory. No module here mutates, renames, moves,
deletes, or reformats anything inside the repository under inspection.
"""
