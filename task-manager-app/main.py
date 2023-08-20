from kivymd.app import MDApp # Импортирует класс MDApp из библиотеки KivyMD для создания приложения
from kivymd.uix.dialog import MDDialog # Импортирует класс диалогового окна MDDialog из KivyMD
from kivymd.uix.boxlayout import MDBoxLayout # Импортирует класс макета MDBoxLayout из KivyMD
from kivymd.uix.pickers import MDDatePicker # Импортирует виджет выбора даты MDDatePicker из KivyMD

from kivymd.uix.list import TwoLineAvatarIconListItem , ILeftBody # импортируется класс TwoLineAvatarIconListItem, элемент списка с аватаркой и двумя строками текста.  Класс ILeftBody, отображение элементов слева в списке 
from kivymd.uix.selectioncontrol import MDCheckbox # импортирует виджет чекбокса MDCheckbox, чтобы можно было использовать его далее при построении интерфейса приложения

from datetime import datetime # Импортирует виджет выбора даты MDDatePicker из KivyMD

from database import Database # Будет добавлено после создания базы данных
db = Database() # создаёт объект класса Database и присваивает его переменной db 

# класс для диалогового окна с полем для отображения даты и кнопкой,
# диалоговое окно получает задачу от пользователя
class DialogContent(MDBoxLayout): # Определяется класс DialogContent, который наследует от MDBoxLayout - это позволит использовать его как содержимое диалогового окна
    # метод init для класса конструктора
    def __init__(self, **kwargs): # конструктор класса, который вызывается при создании объекта
        super().__init__(**kwargs) # Вызов родительского конструктора для инициализации
        self.ids.date_text.text = datetime.now().strftime("%A %d %B %Y") # Устанавливает текст элемента date_text в формате день недели, число, месяц, год

    # метод, показывающая date_picer 
    def show_date_picker(self): # Определяет метод show_date_picker
        date_dialog = MDDatePicker() # Создаёт объект выбора даты
        date_dialog.bind(on_save = self.on_save) # При сохранении даты вызывает метод on_save
        date_dialog.open()

    # метод обрабатывает текущую дату и сохраняет её
    def on_save(self, instance, value, date_range): # Обработчик события выбора даты
        date = value.strftime("%A %d %B %Y") # Формирование даты в нужный вид методом strftime 
        self.ids.date_text.text = str(date) # Устанавливает выбранную дату в элемент date_text

# Класс для пометки и удаления в списке
class ListItemWithCheckBox(TwoLineAvatarIconListItem):
    # Переопределяем конструктор
    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs) # Вызываем конструктор родительского класса
        self.pk = pk # Сохраняем переданный pk как атрибут экземпляра класса

    # Метод для пометки задачи как выполненной 
    def mark(self, check, the_list_item):
        if check.active == True: # Проверяем, активен ли чекбокс
            the_list_item.text = '[s]' + the_list_item.text + '[/s]' # Оборачиваем текст тегами [s][/s] для перечеркивания
            db.mark_task_as_complete(the_list_item.pk) # метод класса db, который используется для пометки задачи в базе данных как отмененной
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk)) # Отмечаем задачу как невыполненную в БД через метод mark_task_as_incomplete, получаем id задачи из атрибута pk

    # Метод для удаления элемента списка задач
    def delete_item(self, the_list_item):
        self.parent.remove_widget(the_list_item) # Удаляем виджет элемента списка из его родительского виджета в интерфейсе через метод remove_widget
        db.delete_task(the_list_item.pk) # Удаляем саму задачу из базы данных, вызывая метод delete_task у объекта класса Database

class LeftCheckbox(ILeftBody, MDCheckbox):
    pass


# Основной App класс
class MainApp(MDApp): # Определяется класс приложения, унаследованный от базового класса MDApp фреймворка KivyMD
    task_list_dialog = None # Cоздаёv глобальную переменную task_list_dialog и инициализирует её значением None, будет содержать диалоговое окно со списком задач
    
    def build(self): # Определяется метод build() - он вызывается при старте приложения
        self.theme_cls.primary_palette = ("Indigo") # установка основной цветовой палитры

    # Метод для отображения диалога создания задачи
    def show_task_dialog(self):
        if not self.task_list_dialog: # Проверяем, был ли уже создан диалог, если нет - создаем его
            self.task_list_dialog = MDDialog( 
                title = "Создать запись", # Заголовок
                type = "custom",
                content_cls = DialogContent() # Класс содержимого
            )
        self.task_list_dialog.open() # Открываем диалог методом open()

    # Метод выполняется при старте приложения, загружает задачи из БД и отображает их 
    def on_start(self):
        try:
            completed_tasks, incompleted_tasks = db.get_tasks()  # Получаем задачи из БД
            
            # Добавляем невыполненные задачи
            if incompleted_tasks != []:
                for task in incompleted_tasks:
                    add_task = ListItemWithCheckBox(pk=task[0],text=task[1], secondary_text=task[2])  # создаем элемент списка на основе данных задачи
                    self.root.ids.container.add_widget(add_task) # добавляем элемент в интерфейс

            # Добавляем выполненные задачи
            if completed_tasks != []:
                for task in completed_tasks:
                    add_task = ListItemWithCheckBox(pk=task[0],text='[s]'+task[1]+'[/s]', secondary_text=task[2]) # помечаем как выполненную в тексте
                    add_task.ids.check.active = True # отмечаем чекбокс как активный
                    self.root.ids.container.add_widget(add_task) # добавляем элемент в интерфейс

        # Обрабатывает исключения (ошибки), которые могут возникнуть при выполнении кода выше
        except Exception as e:
            print(e)
            pass

    # Метод закрывает диалоговое окно по кнопке      
    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()   

    # Метод добавляет новую задачу в БД и интерфейс 
    def add_task(self, task, task_date):
        created_task = db.create_task(task.text, task_date) # Создаем задачу в БД, получаем id и данные  
        self.root.ids['container'].add_widget(ListItemWithCheckBox(pk=created_task[0], text='[b]'+created_task[1]+'[/b]', secondary_text=created_task[2])) # Добавляем новый элемент списка на основе данных из БД
        task.text = '' # Очищаем текстовое поле

if __name__ == "__main__":
    app = MainApp()
    app.run()
