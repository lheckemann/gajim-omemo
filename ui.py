import logging

import gtk

log = logging.getLogger('gajim.plugin_system.omemo')

# from plugins.helpers import log


class PreKeyButton(gtk.Button):
    def __init__(self, plugin, contact):
        super(PreKeyButton, self).__init__(label='Get Missing Prekeys ' + str(
            plugin.are_keys_missing(contact)))
        self.plugin = plugin
        self.contact = contact
        self.connect('clicked', self.on_click)
        self.refresh()

    def refresh(self):
        amount = self.plugin.are_keys_missing(self.contact)
        if amount == 0:
            self.set_no_show_all(True)
            self.hide()
        else:
            self.set_no_show_all(False)
            self.show()
        self.set_label('Missing Prekeys ' + str(amount))

    def on_click(self, widget):
        self.plugin.query_prekey(self.contact)


class ClearDevicesButton(gtk.Button):
    def __init__(self, plugin, contact):
        super(ClearDevicesButton, self).__init__(label='Clear Devices')
        self.plugin = plugin
        self.contact = contact
        self.connect('clicked', self.on_click)

    def on_click(self, widget):
        self.plugin.clear_device_list(self.contact)


class Checkbox(gtk.CheckButton):
    def __init__(self, plugin, chat_control):
        super(Checkbox, self).__init__(label='OMEMO')
        self.chat_control = chat_control
        self.contact = chat_control.contact
        self.plugin = plugin
        self.connect('clicked', self.on_click)

    def on_click(self, widget):
        enabled = self.get_active()
        log.info('Clicked ' + str(enabled))
        if enabled:
            self.plugin.omemo_enable_for(self.contact)
            self.chat_control._show_lock_image(True, 'OMEMO', True, True, True)
        else:
            self.plugin.omemo_disable_for(self.contact)
            self.chat_control._show_lock_image(False, 'OMEMO', False, True,
                                               False)


def _add_widget(widget, chat_control):
    actions_hbox = chat_control.xml.get_object('actions_hbox')
    send_button = chat_control.xml.get_object('send_button')
    send_button_pos = actions_hbox.child_get_property(send_button, 'position')
    actions_hbox.add_with_properties(widget, 'position', send_button_pos - 2,
                                     'expand', False)


class Ui(object):
    def __init__(self, plugin, chat_control):
        contact = chat_control.contact
        self.prekey_button = PreKeyButton(plugin, contact)
        self.checkbox = Checkbox(plugin, chat_control)
        self.clear_button = ClearDevicesButton(plugin, contact)

        enabled = plugin.has_omemo(contact)
        self.toggle_omemo(enabled)
        self.chat_control = chat_control

        _add_widget(self.prekey_button, chat_control)
        _add_widget(self.checkbox, chat_control)
        _add_widget(self.clear_button, chat_control)

    def toggle_omemo(self, enabled):
        if enabled:
            self.checkbox.set_no_show_all(False)
            self.checkbox.show()
        else:
            self.checkbox.set_no_show_all(True)
            self.checkbox.hide()

    def encryption_active(self):
        return self.checkbox.get_active()

    def encryption_disable(self):
        return self.checkbox.set_active(False)

    def activate_omemo(self):
        self.checkbox.set_active(True)
        self.chat_control.print_conversation_line('OMEMO encryption activated',
                                                  'status', '', None)
        self.chat_control._show_lock_image(True, 'OMEMO', True, True, True)

    def plain_warning(self):
        self.chat_control.print_conversation_line(
            'Received plaintext message!', 'status', '', None)

    def update_prekeys(self):
        self.prekey_button.refresh()
