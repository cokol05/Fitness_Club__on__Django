{% extends 'base.html' %}

{% block title %}Управление слотами{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Слоты для персональных тренировок</h1>
        <a href="{% url 'trainers:create_slot' %}" class="btn btn-success">+ Добавить слот</a>
    </div>

    <div class="card">
        <div class="card-body">
            {% if slots %}
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Дата</th>
                                <th>Время</th>
                                <th>Статус</th>
                                <th>Клиент</th>
                                <th>Действие</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for slot in slots %}
                                <tr>
                                    <td>{{ slot.date|date:"d.m.Y" }}</td>
                                    <td>{{ slot.start_time|time:"H:i" }} - {{ slot.end_time|time:"H:i" }}</td>
                                    <td>
                                        {% if slot.is_available %}
                                            <span class="badge bg-success">Доступно</span>
                                        {% else %}
                                            <span class="badge bg-warning">Забронировано</span>
                                        {% endif %}
                                    </td>
                                    <td>{{ slot.client.full_name|default:"—" }}</td>
                                    <td>
                                        <a href="{% url 'trainers:cancel_personal' slot.id %}" class="btn btn-danger btn-sm">Отменить</a>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="text-muted text-center">Нет созданных слотов</p>
            {% endif %}
        </div>
    </div>
    <div class="mt-3">
        <a href="{% url 'trainers:dashboard' %}" class="btn btn-secondary">Назад в панель</a>
    </div>
</div>
{% endblock %}