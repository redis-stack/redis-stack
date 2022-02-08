FROM debian:bullseye-slim

RUN apt-get update -qqy
RUN apt-get upgrade -qqy
ADD ./redis-stack /var/cache/apt/redis-stack/
RUN dpkg -i /var/cache/apt/redis-stack/*.deb
RUN rm -rf /var/cache/apt

CMD ["/opt/redis-stack/bin/redis-server", "/opt/redis-stack/etc/redis-stack.conf"]
