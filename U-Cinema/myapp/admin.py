from django.urls import path, reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from .models import Hall, Movie, User, Session
from .forms import MultiDateSessionForm
from datetime import datetime

class SessionAdmin(admin.ModelAdmin):
    list_display = ("movie", "start_datetime", "ticket_price")
    change_list_template = "admin/session_changelist.html"  # Указываем кастомный шаблон


    def changelist_view(self, request, extra_context=None):
        # Добавляем кнопку в контекст
        extra_context = extra_context or {}
        extra_context["create_sessions_url"] = reverse("admin:create-multiple-sessions")
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("admin/create-multiple-sessions/", self.admin_site.admin_view(self.create_multiple_sessions_view), name="create-multiple-sessions"),
        ]
        return custom_urls + urls

    def create_multiple_sessions_view(self, request):
            if request.method == "POST":
                # Извлекаем данные сеансов
                sessions_data = request.POST.get("sessions", "").split(";")

                movie = request.POST.get("movie")
                ticket_price = request.POST.get("ticket_price")

                for session in sessions_data:
                    if session:
                        date_time_str = session.strip()
                        date_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
                        Session.objects.create(movie_id=movie, start_datetime=date_obj, ticket_price=ticket_price)

                self.message_user(request, "Сеансы успешно созданы!")
                return HttpResponseRedirect("../")

            else:
                form = MultiDateSessionForm()

            return render(request, "admin/create_multiple_sessions.html", {"form": form})
    

    
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "row_number", "seats_per_row", "capacity")
    fields = ("name", "row_number", "seats_per_row", "seating_plan", "capacity")
    readonly_fields = ("capacity",)  # вместимость только для чтения

    def save_model(self, request, obj, form, change):
        # Если изменилось количество рядов или мест в ряду, пересчитываем схему
        if change:  # если объект уже существует (редактируем)
            original_hall = Hall.objects.get(pk=obj.pk)
            if obj.row_number != original_hall.row_number or obj.seats_per_row != original_hall.seats_per_row:
                # Генерация новой схемы на основе новых значений
                obj.seating_plan = {str(i): [1] * obj.seats_per_row for i in range(1, obj.row_number + 1)}

        # Сохраняем вместимость
        obj.capacity = sum(sum(row) for row in obj.seating_plan.values())

        super().save_model(request, obj, form, change)

admin.site.register(Hall, HallAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Movie)
admin.site.register(User)
# TODO: Реализовать проверку при создании сенсов свободен ли зал или выкинуть ошибку 