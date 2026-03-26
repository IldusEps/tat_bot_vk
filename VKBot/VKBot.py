import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

class Bot:
    def __init__(self, token, api_version, handle_default = False):
        self.token = token
        self.vk_session = vk_api.VkApi(token=token, api_version=api_version)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        
        # Словарь с обработчиками команд
        self.commands = {}
        if handle_default:
            self.handle_default = handle_default
        
    def register_command(self, command, handler):
        """Регистрация обработчика команды"""
        self.commands[command] = handler
        
    def send_message(self, user_id, message, keyboard=None, parse_mode=''):
        """Отправка сообщения"""
        try:
            params = {
                "user_id": user_id,
                "message": message,
                "random_id": 0
            }
            if keyboard:
                params["keyboard"] = keyboard.get_keyboard()
            
            self.vk.messages.send(**params)
            # logger.info(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            print("AAAAAA")
            # logger.error(f"Ошибка отправки: {e}")
            
    # def send_keyboard(self, user_id, title, buttons):
    #     """Отправка сообщения с клавиатурой"""
    #     keyboard = VkKeyboard(one_time=False)
        
    #     for button in buttons:
    #         if button.get("color"):
    #             color = getattr(VkKeyboardColor, button["color"].upper())
    #         else:
    #             color = VkKeyboardColor.PRIMARY
                
    #         keyboard.add_button(button["text"], color=color)
    #         if button.get("new_row"):
    #             keyboard.add_line()
                
    #     self.send_message(user_id, title, keyboard)
        
    def run(self):
        """Запуск бота"""
        # logger.info("Бот ВКонтакте запущен!")
        
        for event in self.longpoll.listen():
            print('AA')
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_id = event.user_id
                message = event.text.lower()
                
                # logger.info(f"Сообщение от {user_id}: {message}")
                
                # Ищем обработчик команды
                command_handler = self.commands.get(message)
                if command_handler:
                    command_handler(event)
                else:
                    self.handle_default(self, event, user_id)
                    
    def handle_default(self, message, user_id):
        """Обработчик по умолчанию"""
        self.send_message(user_id, f"Неизвестная команда")

##Иные функции
    def get_user_name(self, user_id):
        """Получение имени и фамилии пользователя"""
        try:
            # Получаем информацию о пользователе
            user_info = self.vk.users.get(
                user_ids=user_id,
                fields='first_name,last_name'
            )[0]
            
            return user_info['first_name'] + " " + user_info['last_name']
        except Exception as e:
            print(f"Ошибка: {e}")
            return None, None