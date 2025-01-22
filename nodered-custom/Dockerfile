# Use the official Node-RED base image
FROM nodered/node-red:latest

# Switch to root for installations
USER root

# Install Node-RED modules with one RUN command to reduce image layers
RUN npm install \
    node-red-dashboard \
    node-red-contrib-coap \
    node-red-node-mysql \
    node-red-contrib-influxdb \
    @meowwolf/node-red-contrib-amqp \
    node-red-node-xmpp \
    && npm cache clean --force

# Switch back to the Node-RED user
USER node-red
