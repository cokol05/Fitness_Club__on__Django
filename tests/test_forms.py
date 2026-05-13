import pytest

@pytest.mark.django_db
class TestCustomUserCreationForm:

    def test_valid_form_data(self):
        from users.forms import CustomUserCreationForm
        form = CustomUserCreationForm(data={
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '+79991234567',
            'birth_date': '2000-01-01',
            'password1': 'strongpass123',
            'password2': 'strongpass123' })
        assert form.is_valid()

    def test_invalid_email(self):
        from users.forms import CustomUserCreationForm
        form = CustomUserCreationForm(data={
            'full_name': 'Test User',
            'email': 'not-an-email',
            'phone': '+79991234567',
            'birth_date': '2000-01-01',
            'password1': 'strongpass123',
            'password2': 'strongpass123' })
        assert not form.is_valid()

    def test_passwords_do_not_match(self):
        from users.forms import CustomUserCreationForm
        form = CustomUserCreationForm(data={
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '+79991234567',
            'birth_date': '2000-01-01',
            'password1': 'strongpass123',
            'password2': 'differentpass'})
        assert not form.is_valid()

    def test_age_too_young(self):
        from users.forms import CustomUserCreationForm
        form = CustomUserCreationForm(data={
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '+79991234567',
            'birth_date': '2020-01-01',
            'password1': 'strongpass123',
            'password2': 'strongpass123'})
        assert not form.is_valid()
        assert '14 лет' in str(form.errors)

    def test_phone_too_short(self):
        from users.forms import CustomUserCreationForm
        form = CustomUserCreationForm(data={
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '123',
            'birth_date': '2000-01-01',
            'password1': 'strongpass123',
            'password2': 'strongpass123'})
        assert not form.is_valid()