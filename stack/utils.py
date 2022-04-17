from .paths import Paths
from typing import Dict
import jinja2

def generate_from_template(src: str, dest: str, template_vars: Dict):
    """Generate a file, from a jinja template."""
    p = Paths(None, None)
    loader = jinja2.FileSystemLoader(p.HERE)
    env = jinja2.Environment(loader=loader)
    tmpl = loader.load(name=src, environment=env)
    with open(dest, "w+") as fp:
        fp.write(tmpl.render(template_vars))
    