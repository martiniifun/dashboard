import reflex as rx
from sqlmodel import select
from collections import Counter


class UserModel(rx.Model, table=True):
    name: str
    email: str
    gender: str


class State(rx.State):
    form_data: dict = {}
    users: list[UserModel] = []

    @rx.event
    def add_user(self, form_data):
        self.form_data = form_data
        with rx.session() as session:
            user = UserModel(
                name=form_data["name"],
                email=form_data["email"],
                gender=form_data["gender"],
            )
            session.add(user)
            session.commit()
            session.refresh(user)  # commit 후에 expired 된 데이터를 다시 불러오기
        self.load_users()

    @rx.event
    def load_users(self):
        """DB에서 전체 사용자 쿼리 → State.users에 저장"""
        with rx.session() as session:
            result = session.exec(select(UserModel))
            self.users = result.all()

    @rx.var
    def users_for_graph(self) -> list[dict]:
        gender_data = Counter(user.gender for user in self.users).items()
        gender_count = [{"name": gender_group, "value": count} for gender_group, count in gender_data]
        print(gender_count)
        return gender_count


import reflex as rx


def index():
    return rx.container(
        rx.vstack(
            rx.box(
                rx.heading("👤 사용자 데이터 대시보드", size="9", color=rx.color("accent", 8)),
                rx.text(
                    "사용자 데이터를 추가하고, 테이블과 그래프로 시각화하세요.",
                    size="4",
                    color=rx.color("gray", 10),
                    margin_top="1em",
                ),
                background="linear-gradient(90deg, #a8edea 0%, #fed6e3 100%)",
                border_radius="2xl",
                box_shadow="lg",
                padding="2.5em",
                margin_bottom="2em",
                align="center",
                width="100%",
            ),

            rx.card(
                rx.form(
                    rx.hstack(
                        rx.input(
                            placeholder="이름",
                            name="name",
                            required=True,
                            size="3",
                            border_radius="lg",
                            background_color=rx.color("gray", 2),
                            width="40%",
                        ),
                        rx.input(
                            placeholder="user@reflex.dev",
                            name="email",
                            size="3",
                            border_radius="lg",
                            background_color=rx.color("gray", 2),
                            width="40%",
                        ),
                        rx.select(
                            ["Male", "Female"],
                            placeholder="성별",
                            name="gender",
                            size="3",
                            border_radius="lg",
                            background_color=rx.color("gray", 2),
                            width="20%",
                        ),
                        spacing="9",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "취소",
                            variant="soft",
                            color_scheme="gray",
                            border_radius="lg",
                            size="4",
                        ),
                        rx.button(
                            "추가",
                            type="submit",
                            variant="solid",
                            color_scheme="teal",
                            border_radius="lg",
                            box_shadow="md",
                            size="4",
                        ),
                        spacing="2",
                        justify="end",
                        margin="1em",
                    ),
                    on_submit=State.add_user,
                    width="100%",
                    padding_y="1em",
                ),
                box_shadow="xl",
                border_radius="2xl",
                background_color=rx.color("gray", 1),
                padding="2em",
                margin_bottom="2em",
                width="100%",
            ),
            rx.hstack(
                rx.card(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("이름"),
                                rx.table.column_header_cell("이메일"),
                                rx.table.column_header_cell("성별"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.users,
                                lambda user: rx.table.row(
                                    rx.table.cell(user.name),
                                    rx.table.cell(user.email),
                                    rx.table.cell(user.gender),
                                    style={"_hover": {"bg": rx.color("accent", 2)}},
                                    align="center",
                                ),
                            ),
                        ),
                        variant="surface",
                        size="3",
                        width="100%",
                    ),
                    box_shadow="xl",
                    border_radius="2xl",
                    background_color="white",
                    padding="2em",
                    margin_bottom="2em",
                    on_mount=State.load_users,
                ),

                rx.card(
                    rx.vstack(
                        rx.heading("성별 분포 차트", size="9", color=rx.color("accent", 8)),
                        rx.recharts.bar_chart(
                            rx.recharts.bar(
                                data_key="value",
                                stroke=rx.color("accent", 9),
                                fill=rx.color("accent", 8),
                            ),
                            rx.recharts.x_axis(data_key="name"),
                            rx.recharts.y_axis(),
                            data=State.users_for_graph,
                            width="100%",
                            height=250,
                        ),
                        align="center",
                        width="100%",
                    ),
                    box_shadow="xl",
                    border_radius="2xl",
                    background="linear-gradient(90deg, #fbc2eb 0%, #a6c1ee 100%)",
                    padding="2em",
                ),
                spacing="3",
                align="center",
                width="100%",
            ),
        ),
        rx.color_mode.button(position="top-right"),
        max_width="880px",
        padding_x="2em",
        padding_y="2em",
        background_color=rx.color("gray", 2),
        border_radius="3xl",
        box_shadow="2xl",
    )


app = rx.App()
app.add_page(index)
