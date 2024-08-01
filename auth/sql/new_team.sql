INSERT INTO external_user (login)
VALUES ('$login')
ON CONFLICT (login) DO NOTHING;
