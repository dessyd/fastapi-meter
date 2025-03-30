# app/test_password.py
from app.auth.password import get_password_hash, verify_password
from app.config import get_settings

# Test basique de hachage et vérification
password = "admin_secure_password"
hashed = get_password_hash(password)
print(f"Original password: {password}")
print(f"Hashed password: {hashed}")
print(f"Verification result: {verify_password(password, hashed)}")

# Test avec le mot de passe admin par défaut


settings = get_settings()
admin_password = settings.INITIAL_ADMIN_PASSWORD
admin_hashed = get_password_hash(admin_password)
print(f"\nAdmin password from config: {admin_password}")
print(f"Admin hashed password: {admin_hashed}")
print(
    "Admin verification result:"
    f" {verify_password(admin_password, admin_hashed)}"
)
