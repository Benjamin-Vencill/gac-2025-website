import os
import random
import re

from typing import List, Tuple


def split_into_segments(content, max_length=700):
    """
    Split content into segments for the notecards.
    Don't break up words or keywords, and also break
    on keywords "Opening Clue" and "Memorable Clues"
    """
    segments = []
    current_segment = []
    current_length = 0
    keywords = ("###", "**Opening", "**Memorable")

    content_words = content.split(" ")
    for word in content_words:
        if word in keywords:
            # Start a new segment before adding the key word
            if current_segment:
                ### Add the segment to the current segment
                s = " ".join(current_segment)
                segments.append(" ".join(current_segment))
                current_segment = []
                current_length = 0
            segments.append(word)
        
        if current_length + len(word) + 1 > max_length:
            segments.append(" ".join(current_segment))
            current_segment = [word]
            current_length = len(word) + 1 # account for spaces
        else:
            current_segment.append(word)
            current_length += len(word) + 1 #account for spaces

    if current_segment:
        segments.append(" ".join(current_segment))
    
    return [segment for segment in segments if segment not in keywords]


def render_markdown_elements(segment: str) -> str:
    """
    Strip the segment of all markdown semantics
    """
    segment = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', segment)  # Bold

    return segment


def render_html_document(n: int, html_bodies: List[str], output_dir: str) -> None:
    """
    Create an HTML Document from the html_bodies
    """
    template = """<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>GAC History</title>
            <link rel="stylesheet" href="../styles/gac-history-notecards.css">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Averia+Libre:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&family=Special+Elite&display=swap" rel="stylesheet">
        </head>
        <body>
            <div class="note-container note-container-first">
                {noteBodies}
            </div>
        </body>
        <script>
        function addNotebookPage() {
            // Get the main container for the notebook pages
            const notes = document.getElementsByClassName('note-container');

            for (let noteContainer of notes) {
                // Get dimensions
                const containerHeight = noteContainer.offsetHeight;
                const containerWidth = noteContainer.offsetWidth;

                // Create a new notebook page
                const newPage = document.createElement('div');
                newPage.classList.add('notebook-paper');
                newPage.classList.add('notebook-paper-a')
                newPage.classList.add('notebook-paper.background');

                // Optional: Add some content to the new page
                newPage.innerHTML = '<p></p>';

                // Set random positioning for the new page
                const randomX = Math.floor((Math.random() -0.5) * (containerWidth + 1));
                const randomY = Math.floor(Math.random() * (containerHeight / 2  + 1));
                const randomRotation = Math.random() * 360; // Random rotation (-10 to 10 degrees)

                newPage.style.position = 'absolute';
                newPage.style.transform = `translate(${randomX}%, ${-randomY}%) rotate(${randomRotation}deg)`;
                newPage.style.zIndex = 0; // Random z-index to place behind/above others

                noteContainer.appendChild(newPage)
            }
        }

        // Call the function to add a few pages dynamically
        for (let i = 0; i < 100; i++) {
            addNotebookPage();
        }
        </script>
    </html>
    """

    html_body = "\n".join(html_bodies)
    html_document = template.replace("{noteBodies}", html_body)
    with open(f"{output_dir}/gac-history-{n}.html", "w") as f:
        f.write(html_document)

def render_html_body_template(segment: str) -> str:
    """
    Fill body template
    """

    template = """
    <div class="notebook-paper {bodyDisplayType}">
        <p class="notebook-paper-body-text">{bodyText}</p>
    </div>
    """
    if random.random() < 0.5:
        display_type = "notebook-paper-b"
    else:
        display_type = "notebook-paper-a"
    template = template.replace("{bodyDisplayType}", display_type)
    template = template.replace("{bodyText}", segment)

    return template

def render_html_title_template(segment: str) -> str:
    """
    Fill title template
    """

    template = """    
    <div class="notebook-paper {bodyDisplayType}">
        <h2 class="notebook-paper-title-text">{sectionTitle}</h2>
        <p class="notebook-paper-body-text">{bodyText}</p>
    </div>
    """

    match = re.search(r"###\s*(\d{4})", segment)
    segment = segment.replace("###", "")
    if match:
        title = match.group(1)
        template = template.replace("{sectionTitle}", title)
        if random.random() < 0.5:
            display_type = "notebook-paper-b"
        else:
            display_type = "notebook-paper-a"
        template = template.replace("{bodyDisplayType}", display_type)
        template = template.replace("{bodyText}", segment)
    else:
        template = render_html_body_template(segment)

    return template
        

if __name__ == "__main__":
    # Read the Markdown file
    input_file = "gac-history-original.md"
    output_dir = "gac-history"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read the markdown content
    with open(input_file, "r", encoding="utf-8") as file:
        markdown_content = file.read()
    
    markdown_content = markdown_content.replace("\n", " ")
    
    segments = split_into_segments(markdown_content)

    html_bodies = []
    n_documents = 0
    n_sections_rendered = 0

    for segment in segments:
        segment = render_markdown_elements(segment)
        if segment.startswith("###"):
            # Create a new HTML document. We want 1 title section per document
            if html_bodies and n_sections_rendered % 3 == 0:
                document = render_html_document(n_documents, html_bodies, output_dir)
                n_documents += 1
                html_bodies = []
            html = render_html_title_template(segment)
            n_sections_rendered += 1
        else:
            html = render_html_body_template(segment)

        html_bodies.append(html)
    
    if html_bodies:
        document = render_html_document(n_documents, html_bodies, output_dir)
    

    
            

