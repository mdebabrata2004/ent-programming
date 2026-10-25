"""
ENT Web subsystem: Static website generation, HTML/CSS builder, and local execution server.
"""

from ent.web.builder import build_website_from_file, build_website_from_source, GeneratedWebsite

__all__ = ["build_website_from_file", "build_website_from_source", "GeneratedWebsite"]
