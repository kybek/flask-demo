class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    firstname: Mapped[str]
    middlename: Mapped[str]
    lastname: Mapped[str]
    birthdate: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
