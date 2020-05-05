# This is a work-in-progress showing a way to move the
# view-related codebase into an "output-like" format.
from jinja2 import Environment, FileSystemLoader

def render(template, data):
    """ render("user.yaml", g.get_user())
        > "frobnitzem:"
        > "  
    """
    file_loader = FileSystemLoader('views')
    env = Environment(loader=file_loader)

    template = env.get_template(template)

    return template.render(persons=persons)

