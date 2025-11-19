import secrets

# Generate a secure random SECRET_KEY for JWT
secret_key = secrets.token_hex(32)

print("=" * 60)
print("🔐 SECRET_KEY cho JWT Authentication")
print("=" * 60)
print("\nCopy dòng dưới đây và paste vào Environment Variables của Render:\n")
print(f"SECRET_KEY={secret_key}")
print("\n" + "=" * 60)
print("⚠️  LƯU Ý: Không chia sẻ key này với ai!")
print("=" * 60)
