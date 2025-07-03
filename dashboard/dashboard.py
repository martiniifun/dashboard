import reflex as rx


class State(rx.State):
    form_data: dict = {}
    users:list[dict] = []

    def handle_data(self, form_data):
        self.form_data = form_data
        self.users.append(self.form_data)


def index():
    return rx.container(
        rx.text(State.form_data),
        rx.form(
            rx.input(
                placeholder="User Name",
                name="name",
                required=True,
            ),
            rx.input(
                placeholder="user@reflex.dev",
                name="email",
            ),
            rx.select(
                ["Male", "Female"],
                placeholder="male",
                name="gender",
            ),
            rx.button(
                "Cancel",
                variant="soft",
                color_scheme="gray",
            ),
            rx.button(
                "Submit", type="submit"
            ),
            on_submit=State.handle_data,
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Name"),
                    rx.table.column_header_cell("Email"),
                    rx.table.column_header_cell("Gender"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.users,
                    lambda user: rx.table.row(rx.table.cell(user.name), rx.table.cell(user.email), rx.table.cell(user.gender)),
                ),
            ),
        ),
    )


app = rx.App()
app.add_page(index)
