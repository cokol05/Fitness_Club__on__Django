{% extends 'base.html' %}

{% block title %}Панель тренера{% endblock %}

{% block content %}
<div class="container py-5">
    <h1 class="text-center mb-4">Панель управления тренера</h1>
    <p class="text-center mb-5">Добро пожаловать, {{ user.full_name }}!</p>

    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Мои групповые тренировки</h4>
                </div>
                <div class="card-body">
                    {% if schedules %}
                        <ul class="list-group">
                            {% for schedule in schedules %}
                                <li class="list-group-item">
                                    <strong>{{ schedule.workout.name }}</strong><br>
                                    {{ schedule.club.name }} - {{ schedule.date|date:"d.m.Y" }} {{ schedule.start_time|time:"H:i" }}
                                    <small class="d-block text-muted">Записано: {{ schedule.booked_places }} / {{ schedule.workout.max_participants }}</small>
                                </li>
                            {% endfor %}
                        </ul>
                    {% else %}
                        <p class="text-muted">Нет предстоящих групповых тренировок</p>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Персональные тренировки</h4>
                </div>
                <div class="card-body">
                    <a href="{% url 'trainers:personal_slots' %}" class="btn btn-primary mb-3">
                        <i class="fas fa-calendar-alt"></i> Перейти к управлению слотами
                    </a>
                    <ul class="list-group">
                        {% for pt in personal_trainings %}
                            <li class="list-group-item">
                                <div>
                                    <strong>{{ pt.date|date:"d.m.Y" }}</strong> {{ pt.start_time|time:"H:i" }} - {{ pt.end_time|time:"H:i" }}
                                    {% if pt.client %}
                                        <br><small class="text-success">Клиент: {{ pt.client.full_name }}</small>
                                    {% else %}
                                        <br><small class="text-warning">Свободно</small>
                                    {% endif %}
                                </div>
                                <!-- Кнопка удаления УДАЛЕНА - она есть в управлении слотами -->
                            </li>
                        {% empty %}
                            <li class="list-group-item text-muted">Нет созданных слотов</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}