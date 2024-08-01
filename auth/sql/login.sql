SELECT user_id, user_group
FROM internal_user
WHERE login = '$login' AND password = '$password';
