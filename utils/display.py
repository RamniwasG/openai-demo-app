from IPython.display import Markdown, display

def print_markdown(text: str):
    display(Markdown(text))

# Example usage:
# print_markdown("# Hello World\nThis is a markdown message.")
def render_display(text: str, type: str = "rich"):
    if type == "markdown":
        print_markdown(text)
    elif type == "rich":
        try:
            from rich import print
            from rich.markdown import Markdown
            print(Markdown(text))
        except ImportError:
            print(text)
    else:
        print(text)

# render_display("# AI Agent")
# render_display("## Checking...")
# render_display("Result: **Success**")