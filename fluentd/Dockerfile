FROM fluent/fluentd:latest

# Install MongoDB plugin
RUN apk add --update --virtual .build-deps \
        sudo build-base ruby-dev \
 && sudo gem install fluent-plugin-mongo \
 && sudo gem sources --clear-all \
 && apk del .build-deps \
 && rm -rf /var/cache/apk/* \
           /home/fluent/.gem/ruby/2.3.0/cache/*.gem

COPY fluentd_mongo.conf /fluentd/etc/
ENV FLUENTD_CONF fluentd_mongo.conf
