import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import action, row_action
from starlette_admin.contrib.sqla import Admin, ModelView

from db.model import engine, User, session
from web.provider import UsernameAndPasswordProvider

app = Starlette()

admin = Admin(engine,
              title="Ortiqboyev Market Admin Panel",
              base_url='/',
              auth_provider=UsernameAndPasswordProvider(),
              middlewares=[Middleware(SessionMiddleware, secret_key="qewrerthytju4")])


class UsersModelView(ModelView):
    """
    Foydalanuvchilar uchun ModelView
    """
    fields = [
        'id',
        'first_name',
        'last_name',
        'middle_name',
        'gender',
        'birth_date',
        'address',
        'phone_number',
        'username',
        'seria_number',
        'debt',
        'start_debt',
        'end_debt',
        'is_active',
        'created_at',
    ]

    exclude_fields_from_list = ["photo", "middle_name", "updated_at"]
    exclude_fields_from_create = ["created_at", "updated_at", "is_active"]
    exclude_fields_from_edit = ["created_at", "id"]

    searchable_fields = ['first_name', 'last_name', 'phone_number', 'username', 'seria_number']
    sortable_fields = ['id', 'first_name', 'last_name', 'created_at', 'debt']

    # Filterlar
    filters = [
        "is_active",
        "gender",
        ("debt", "Qarz bor", lambda: User.debt > 0),
        ("debt", "Qarz yo'q", lambda: User.debt == 0),
    ]

    # Formatlar
    def format_first_name(self, request, obj, field):
        return f"👤 {obj.first_name}" if obj.first_name else "Noma'lum"

    def format_phone_number(self, request, obj, field):
        return f"📱 {obj.phone_number}" if obj.phone_number else "Noma'lum"

    def format_debt(self, request, obj, field):
        if obj.debt > 0:
            return f"💳 {obj.debt:,.0f} so'm"
        return "💰 Qarz yo'q"

    def format_is_active(self, request, obj, field):
        if obj.is_active:
            return "🟢 Faol"
        return "🔴 Nofaol"

    # Harakatlar
    @action(
        name="make_active",
        text="Faollashtirish",
        confirmation="Foydalanuvchini faollashtirishni xohlaysizmi?",
        submit_btn_text="Ha",
        submit_btn_class="btn-success",
    )
    async def make_active_action(self, request, pks):
        """Foydalanuvchilarni faollashtirish"""
        for user in await self.find_by_pks(request, pks):
            user.is_active = True
        session.commit()
        return f"{len(pks)} ta foydalanuvchi faollashtirildi"

    @action(
        name="make_inactive",
        text="Nofaollashtirish",
        confirmation="Foydalanuvchini nofaollashtirishni xohlaysizmi?",
        submit_btn_text="Ha",
        submit_btn_class="btn-danger",
    )
    async def make_inactive_action(self, request, pks):
        """Foydalanuvchilarni nofaollashtirish"""
        for user in await self.find_by_pks(request, pks):
            user.is_active = False
        session.commit()
        return f"{len(pks)} ta foydalanuvchi nofaollashtirildi"

    @action(
        name="clear_debt",
        text="Qarzni tozalash",
        confirmation="Qarzni nolga tushirishni xohlaysizmi?",
        submit_btn_text="Ha",
        submit_btn_class="btn-warning",
    )
    async def clear_debt_action(self, request, pks):
        """Qarzlarni tozalash"""
        for user in await self.find_by_pks(request, pks):
            user.debt = 0.0
            user.start_debt = None
            user.end_debt = None
        session.commit()
        return f"{len(pks)} ta foydalanuvchining qarzi tozalandi"

    @row_action(
        name="view_details",
        text="Batafsil",
        icon_class="fas fa-eye",
    )
    async def view_details_action(self, request, pk):
        """Foydalanuvchi ma'lumotlarini ko'rish"""
        user = await self.find_by_pk(request, pk)
        return f"""
        <h4>👤 Foydalanuvchi ma'lumotlari</h4>
        <table class="table table-bordered">
            <tr><th>ID:</th><td>{user.id}</td></tr>
            <tr><th>Ism:</th><td>{user.first_name or 'Noma\'lum'}</td></tr>
            <tr><th>Familiya:</th><td>{user.last_name or 'Noma\'lum'}</td></tr>
            <tr><th>Telefon:</th><td>{user.phone_number or 'Noma\'lum'}</td></tr>
            <tr><th>Passport:</th><td>{user.seria_number or 'Noma\'lum'}</td></tr>
            <tr><th>Qarz:</th><td>{user.debt:,.0f} so'm</td></tr>
            <tr><th>Holat:</th><td>{'🟢 Faol' if user.is_active else '🔴 Nofaol'}</td></tr>
            <tr><th>Ro'yxatdan o'tgan:</th><td>{user.created_at.strftime('%d.%m.%Y %H:%M')}</td></tr>
        </table>
        """


# ModelView ni admin panelga qo'shamiz
admin.add_view(UsersModelView(User, label="Foydalanuvchilar", icon="fa fa-users"))

# Admin panelni asosiy app ga mount qilamiz
admin.mount_to(app)

if __name__ == '__main__':
    uvicorn.run("admin_panel:app", host="127.0.0.1", port=8000, reload=True)