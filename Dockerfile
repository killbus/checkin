FROM python:3.7-slim

ENV TZ=Asia/Shanghai

WORKDIR /tmp

COPY requirements.txt requirements.txt

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		tini \
        cron \
	; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    \
    savedAptMark="$(apt-mark showmanual)"; \
    apt-get update; \
	apt-get install -y --no-install-recommends \
        gcc \
    ; \
    rm -r /var/lib/apt/lists/*; \
    pip install -r requirements.txt; \
    \
# reset apt-mark's "manual" list so that "purge --auto-remove" will remove all build dependencies
	apt-mark auto '.*' > /dev/null; \
	[ -z "$savedAptMark" ] || apt-mark manual $savedAptMark; \
	find /usr/local -type f -executable -exec ldd '{}' ';' \
		| awk '/=>/ { print $(NF-1) }' \
		| sort -u \
		| xargs -r dpkg-query --search \
		| cut -d: -f1 \
		| sort -u \
		| xargs -r apt-mark manual \
	; \
	apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false;

SHELL ["/bin/bash","-c","-l"]
RUN set -eux; \
    \
    declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env; \
    echo "SHELL=/bin/bash" > /var/spool/cron/crontabs/root; \
    echo "BASH_ENV=/container.env" >> /var/spool/cron/crontabs/root; \
    echo "0 */1 * * * /usr/bin/flock -n /tmp/fcj.lockfile python /usr/src/app/discuz/discuz.py > /proc/1/fd/1 2>/proc/1/fd/2" >> /var/spool/cron/crontabs/root; \
    crontab /var/spool/cron/crontabs/root; 

COPY entrypoint.sh /

RUN chmod +x /entrypoint.sh

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT [ "/entrypoint.sh" ]