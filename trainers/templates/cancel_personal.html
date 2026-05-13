{% extends 'base.html' %}

{% block title %}Отмена персональной тренировки{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-md-6 mx-auto">
            <div class="card">
                <div class="card-header bg-danger text-white">
                    <h3 class="mb-0">Отмена персональной тренировки</h3>
                </div>
                <div class="card-body">
                    <p>Вы уверены, что хотите отменить эту персональную тренировку?</p>

                    <div class="alert alert-warning">
                        <p><strong>Дата:</strong> {{ pt.date|date:"d.m.Y" }}</p>
                        <p><strong>Время:</strong> {{ pt.start_time|time:"H:i" }} - {{ pt.end_time|time:"H:i" }}</p>
                        {% if pt.client %}
                            <p><strong>Клиент:</strong> {{ pt.client.full_name }}</p>
                        {% else %}
                            <p><strong>Клиент:</strong> не назначен</p>
                        {% endif %}
                    </div>

                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label for="reason" class="form-label">Причина отмены (необязательно)</label>
                            <textarea name="reason" id="reason" class="form-control" rows="3"></textarea>
                        </div>
                        <button type="submit" class="btn btn-danger w-100">Подтвердить отмену</button>
                        <a href="{% url 'trainers:personal_slots' %}" class="btn btn-secondary w-100 mt-2">Назад</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}