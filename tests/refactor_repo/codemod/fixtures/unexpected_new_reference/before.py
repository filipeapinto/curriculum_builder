"""Fixture: unexpected curriculum_factory reference not created by rewrite."""
import curriculum_factory


def use_unexpected():
    return curriculum_factory.something()
