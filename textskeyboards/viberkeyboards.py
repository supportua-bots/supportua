from vibertelebot.utils.tools import keyboard_consctructor

LOGO = 'https://i.ibb.co/82bQQtt/download.png'

end_chat_keyboard = keyboard_consctructor([
            ('Завершити чат', 'end_chat', '')
            ])

menu_keyboard = keyboard_consctructor([
            ("Оформити заявку на ремонт", 'repair', ''),
            ('Зарееструвати сервiс', 'register', ''),
            ("Зв'язок з оператором", 'operator', ''),
            ])

confirmation_keyboard = keyboard_consctructor([
            ("Зв'язок з оператором", 'operator', ''),
            ('Продовжити', 'continue', '')
            ])

photo_keyboard = keyboard_consctructor([
            ('Пропустити', 'guarantee', ''),
            ('Продовжити', 'upload', '')
            ])

operator_keyboard = keyboard_consctructor([
            ("Зв'язок з оператором", 'operator', '')
            ])

upload_keyboard = keyboard_consctructor([
            ("Зв'язок з оператором", 'operator', ''),
            ("Продовжити", 'upload', '')
            ])

return_keyboard = keyboard_consctructor([
            ('Меню', 'menu', '')
            ])

pay_keyboard = keyboard_consctructor([
            ("Зв'язок з оператором", 'operator', ''),
            ('Я оплатив', 'paid', '')
            ])

phone_keyboard = [
            ("Зв'язок з оператором", 'operator', ''),
            ('Подiлитись номером', 'phone_reply', '')
            ]
