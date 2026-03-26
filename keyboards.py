from vk_api.keyboard import VkKeyboard, VkKeyboardColor

ADMINS = [40776490300, 21500184400]

# class NewInlineKeyboard(VkKeyboard):
#     def __init__(self, *args: tuple,  row_width=1, one_time=False):
#         super().__init__(row_width=row_width, one_time=one_time)
#         for buttons in args:
#             if isinstance(buttons[0], tuple):
#                 self.add(*[types.InlineKeyboardButton(button[0], callback_data=button[1])
#                          for button in buttons])
#             else:
#                 self.add(types.InlineKeyboardButton(
#                     buttons[0], callback_data=buttons[1]))

#     def add_button(self, *args):
#         self.add(types.KeyboardButton(args))


class NewKeyboard(VkKeyboard):
    def __init__(self, *args: tuple, one_time=False):
        super().__init__(one_time=one_time)
        for i, buttons in enumerate(args):
            if isinstance(buttons, list):
                if i != 0:
                    self.add_line()                
                for button in buttons:
                    self.add_button(button, color=VkKeyboardColor.PRIMARY)
            else:
                self.add_button(buttons, color=VkKeyboardColor.PRIMARY)


# Клавиатура опроса при старте бота
StartKeyboard = NewKeyboard(('Нашел в поиске', 'Start_search'), (
    'Перешел из канала', 'Start_group'), ('Другое', 'Start_others'))

# Основная клавиатура
MainKeyboard = NewKeyboard('🎲 Случайное слово',
                           '🈳 Сменить язык', '⚠️ Сообщить о проблеме')

# Клавиатура "сообщить о проблеме"
ReportKeyboard = NewKeyboard('Назад')

# Клавиатура "Устранить проблему"
AdminKeyboard = NewKeyboard('🎲 Случайное слово',
                            '🈳 Сменить язык',  ['Перезапуск бота', 'Логи'], ['⚠️ Сообщить о проблеме', 'Статистика'])


def mainKeyboard(message):
    user_id = message if isinstance(message, int) else message.user_id
    return AdminKeyboard if user_id in ADMINS else MainKeyboard
