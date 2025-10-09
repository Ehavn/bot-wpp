FROM rabbitmq:3.11-management

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV DELAYED_PLUGIN_VERSION=3.12.0

RUN curl -L -o /opt/rabbitmq/plugins/rabbitmq_delayed_message_exchange-${DELAYED_PLUGIN_VERSION}.ez \
    https://github.com/rabbitmq/rabbitmq-delayed-message-exchange/releases/download/v${DELAYED_PLUGIN_VERSION}/rabbitmq_delayed_message_exchange-${DELAYED_PLUGIN_VERSION}.ez && \
    rabbitmq-plugins enable --offline rabbitmq_delayed_message_exchange && \
    apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
