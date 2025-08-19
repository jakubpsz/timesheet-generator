
from flask import Blueprint

# Main site blueprint
bp = Blueprint("main", __name__, template_folder="templates/htm", static_folder="static")

from . import routes  # noqa: E402,F401  (register routes)
