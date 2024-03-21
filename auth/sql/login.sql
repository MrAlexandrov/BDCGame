select user_id, user_group
from jackbox.internal_user
where login = '$login' and password = '$password'