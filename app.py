import webbrowser
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Label
from todoist_api_python.api import TodoistAPI


class TokenSetter(Screen):
    """Input screen for setting the token"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path: Path = self.app.TOKEN_PATH

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Api token (press shift to enable copy-paste)", password=True, classes="token_input")
        yield Footer()

    @on(Input.Submitted, selector=".token_input")
    def store_input(self, event: Input.Submitted) -> None:
        self.path.touch(exist_ok=True)
        with self.path.open(mode="w") as file:
            file.write(event.value)

        self.app.token = event.value
        self.app.switch_mode("task")


class TaskQuickAdd(Screen):
    """Input screen for adding a task to Todoist"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.todo = TodoistAPI(self.app.token)
        self.input_field = Input(placeholder="write a task", classes="task")
        self.label = Label()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.input_field
        yield self.label
        yield Footer()

    @on(Input.Submitted, selector=".task")
    def send_quick_task(self, event: Input.Submitted) -> None:
        if event.value:
            self.input_field.clear()
            result = self.todo.quick_add_task(event.value)
            self.label.update(
                f"Added task '{result.task.content}' to project `{result.resolved_project_name}` "
                f"\n[@click=go_to_link('{result.task.url}')]Go to task[/]"
            )
        else:
            self.label.update("Empty task provided...")


class QuickAdd(App):
    """Main app, which checks the token file and sets the bindings"""

    # CSS_PATH = ""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    MODES = {
        "token": TokenSetter,
        "task": TaskQuickAdd,
    }
    TITLE = "Todoist Quick Add"
    SUB_TITLE = "written by Ruben"
    TOKEN_PATH = Path("token.txt")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = self.get_token()

    def get_token(self) -> str:
        return self.TOKEN_PATH.read_text() if self.TOKEN_PATH.exists() else ""

    def on_mount(self) -> None:
        if self.token:
            self.switch_mode("task")
        else:
            self.switch_mode("token")

    @staticmethod
    def action_go_to_link(url: str):
        webbrowser.open_new(url)


if __name__ == "__main__":
    app = QuickAdd()
    app.run()
