import multiprocessing
import os


formula_result = (multiprocessing.cpu_count() * 2) + 1
gunicorn_logs_dir = '{{ gunicorn_logs_dir }}'

bind = '{{ gunicorn_socket }}'
workers = formula_result
threads = formula_result
chdir = '{{ current_symlink }}'
pidfile = '{{ gunicorn_pidfile }}'
user = '{{ remote_user }}'
# http://docs.gunicorn.org/en/stable/settings.html#secure-scheme-headers and forwarded_allow_ips
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
# forwarded_allow_ips = '{{ ansible_default_ipv4.address }}'
accesslog = os.path.join(gunicorn_logs_dir, 'access.log')
errorlog = os.path.join(gunicorn_logs_dir, 'error.log')
