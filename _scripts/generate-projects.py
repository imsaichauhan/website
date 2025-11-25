#!/usr/bin/env python3
"""
Script to generate projects/index.qmd from individual project files
Run this whenever you add/modify projects by running:

python3 generate-projects.py

"""

import re
from pathlib import Path

# Define project order (first one is featured)
PROJECT_ORDER = [
    "rice",
    "rivers-battlefields",
    "sunscreen-planet",
    "antibody-production",
    "science-outsiders",
    "death-rays",
    "building-cities",
    "energy-storage",
]

def parse_yaml_frontmatter(content):
    """Simple YAML parser for our specific use case"""
    if not content.startswith('---'):
        return {}
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    frontmatter = parts[1].strip()
    metadata = {}
    
    for line in frontmatter.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            metadata[key] = value
    
    return metadata

def load_project_metadata(project_name):
    """Load metadata from a project's index.qmd file"""
    project_file = Path(f"projects/{project_name}/index.qmd")
    if not project_file.exists():
        return None
    
    with open(project_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata = parse_yaml_frontmatter(content)
    
    return {
        'title': metadata.get('title', 'Untitled'),
        'description': metadata.get('description', ''),
        'tag': metadata.get('tag', ''),
        'image': metadata.get('image', ''),
        # preserve original image URL separately so we don't overwrite it
        'image_original': metadata.get('image', ''),
        # include project directory name so generators can look for local assets
        'name': project_name,
        'link': f'/projects/{project_name}/'
    }

def generate_projects_page():
    """Generate the projects/index.qmd file"""
    
    # Load all projects
    projects = []
    for project_name in PROJECT_ORDER:
        metadata = load_project_metadata(project_name)
        if metadata:
            projects.append(metadata)
    
    if not projects:
        print("No projects found!")
        return
    
    # Featured project (first one)
    featured = projects[0]
    grid_projects = projects[1:]
    # Prefer a local downloaded image if available (saved to _assets/images/projects/)
    assets_dir = Path("_assets/images/projects")
    for p in projects:
        name = p.get('name')
        if not name:
            continue
        candidates = list(assets_dir.glob(f"{name}.*")) if assets_dir.exists() else []
        if candidates:
            # use the first candidate and set a local_image path (relative from projects/index.qmd)
            p['local_image'] = str(Path("..") / "_assets" / "images" / "projects" / candidates[0].name)
        else:
            p['local_image'] = None

    # Preload the featured project's image to improve LCP for the index page.
    # Prefer the downloaded local image if present, otherwise fall back to the original URL.
    preload_href = featured.get('local_image') or featured.get('image_original') or featured.get('image')
    preload_link = f"    <link rel=\"preload\" as=\"image\" href=\"{preload_href}\">"

    # For the visible featured image in the generated index, use the local image
    # when available so the page serves the local asset end-to-end. Keep the
    # original web URL in project frontmatter (`image` / `image_original`) for
    # reference and attribution.
    displayed_image = featured.get('local_image') or featured.get('image_original') or featured.get('image')
    # Generate the QMD file
    output = (
        "---\n"
        "title: \"\"\n"
        "---\n\n"
        "```{=html}\n"
        "<!-- Preload featured image for faster loading -->\n"
        + preload_link + "\n"
        "```\n\n"
        "::: {.projects-layout}\n"
        "::: {.featured-project}\n"
        "::: {.featured-image}\n"
        "[![](" + featured['image'] + ")](" + featured['link'] + ")\n"
        ":::\n"
        "::: {.featured-content}\n"
        "::: {.featured-title}\n"
        "[" + featured['title'] + "](" + featured['link'] + ")\n"
        ":::\n"
        "::: {.featured-separator}\n"
        ":::\n"
        "::: {.featured-description-wrapper}\n"
        "::: {.featured-description}\n"
        + featured['description'] + "\n"
        ":::\n"
        "::: {.featured-read-more}\n"
        "[Read more →](" + featured['link'] + ")\n"
        ":::\n"
        ":::\n"
        "::: {.featured-separator}\n"
        ":::\n"
        "::: {.featured-tag}\n"
        + featured['tag'] + "\n"
        ":::\n"
        "::: {.featured-separator}\n"
        ":::\n"
        ":::\n"
        ":::\n\n"
        "::: {.projects-grid}\n"
    )
    
    # Add grid projects
    for project in grid_projects:
        output += """::: {.project-grid-card}
::: {.project-grid-title}
[""" + project['title'] + """](""" + project['link'] + """)
:::
::: {.project-grid-separator}
:::
::: {.project-grid-description}
""" + project['description'] + """
:::
::: {.project-grid-read-more}
[Read more →](""" + project['link'] + """)
:::
::: {.project-grid-separator}
:::
::: {.project-grid-tag}
""" + project['tag'] + """
:::
:::

"""
    
    output += """:::
:::
"""
    
    # Write to file
    with open('projects/index.qmd', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✅ Generated projects/index.qmd with {len(projects)} projects")
    print(f"   Featured: {featured['title']}")
    print(f"   Grid: {len(grid_projects)} projects")

if __name__ == '__main__':
    generate_projects_page()
