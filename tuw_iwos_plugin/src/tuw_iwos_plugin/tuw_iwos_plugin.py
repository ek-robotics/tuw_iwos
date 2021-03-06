#!/usr/bin/env python3

import os
import rospkg
from tuw_iwos_plugin.handler.stop_handler import StopHandler
from tuw_iwos_plugin.handler.publisher_handler import PublisherHandler
from tuw_iwos_plugin.handler.steering_handler import SteeringHandler
from tuw_iwos_plugin.handler.revolute_handler import RevoluteHandler
from qt_gui.plugin import Plugin
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget
from tuw_nav_msgs.msg import JointsIWS


class IWOSPlugin(Plugin):
    """
    class to publish messages based on UI
    """

    def __init__(self, context):
        super(IWOSPlugin, self).__init__(context)
        # setup plugin
        self.setObjectName('IWOSPlugin')
        self._widget = QWidget()
        ui_file = os.path.join(rospkg.RosPack().get_path('tuw_iwos_plugin'),
                               'resource',
                               'iwos_plugin.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('IWOSPluginUI')
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

        self.stop_handler = StopHandler(self, self._widget)
        self.publisher_handler = PublisherHandler(self, self._widget)
        self.steering_handler = SteeringHandler(self, self._widget)
        self.revolute_handler = RevoluteHandler(self, self._widget)
        return

    def publish_message(self):
        """
        creates and publishes a JointIWS message
        steering and revolute command are fetched from UI if stop is disabled, or are zero if stop is enabled
        :return:
        """
        message = JointsIWS()
        if self.stop_handler.stop() is False:
            message.type_steering = "cmd_position"  # rad
            message.type_revolute = "cmd_velocity"  # m/s
            message.steering = self.steering_handler.fetch_values()
            message.revolute = self.revolute_handler.fetch_values()

        if self.stop_handler.stop() is True:
            message.type_steering = "cmd_torque"  # nm
            message.type_revolute = "cmd_velocity"  # m/s
            message.steering = [0.0, 0.0]
            message.revolute = [0.0, 0.0]

        self.publisher_handler.publish(message)

    def enable_stop_mode(self):
        """
        enables stop mode
        in stop mode stop button turns red, other UI elements are disables, messages sent contain only zero
        :return:
        """
        self.publish_message()
        self.publisher_handler.disable()
        self.steering_handler.disable()
        self.revolute_handler.disable()

    def disable_stop_mode(self):
        """
        disables stop mode
        in stop mode stop button turns red, other UI elements are disables, messages sent contain only zero
        :return:
        """
        self.publisher_handler.enable()
        self.steering_handler.enable()
        self.revolute_handler.enable()

    def shutdown_plugin(self):
        self.publisher_handler.unregister_publisher()
        return
