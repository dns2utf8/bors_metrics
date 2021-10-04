HOST = "web_bors-metrics.estada.ch@lich.estada.ch"

setup: venv
	. venv/bin/activate && pip install prometheus-client beautifulsoup4 requests

deploy: setup
	rsync -avz --delete-after fetch_bors_metrics.py run_server.sh venv ${HOST}:

ssh:
	ssh ${HOST}

venv:
	python3 -m venv venv

systemd_setup:
	ssh ${HOST} "mkdir -p ~/.config/systemd/user/"
	rsync bors_metrics.service bors_metrics.timer ${HOST}:~/.config/systemd/user/
	ssh ${HOST} -t "systemctl --user daemon-reload ; systemctl --user restart bors_metrics.service ; systemctl --user enable bors_metrics.service ; systemctl --user enable bors_metrics.timer ; systemctl --user start bors_metrics.timer ; systemctl --user status bors_metrics.service ; systemctl --user status bors_metrics.timer"

systemd_stop:
	ssh ${HOST} -t "systemctl --user stop bors_metrics.service ; systemctl --user status bors_metrics.service"

systemd_restart:
	ssh ${HOST} -t "systemctl --user restart bors_metrics.service ; systemctl --user status bors_metrics.service"