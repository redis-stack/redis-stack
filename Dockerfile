FROM debian:bullseye-slim

RUN apt-get update -qqy
RUN apt-get upgrade -qqy
ADD ./redis-stack /var/cache/apt/redis-stack/
COPY ./scripts/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
RUN dpkg -i /var/cache/apt/redis-stack/*.deb
RUN rm -rf /var/cache/apt

EXPOSE 6379 8081

ENTRYPOINT ["/entrypoint.sh"]