import sqlite3 # SQLite - это встроенная реляционная СУБД, реализованная на языке C и входящая в состав Python

# Создание класса Database()
class Database():
    # Конструктор класса Database. Выполняет подключение и инициализацию
    def __init__(self):
        self.con = sqlite3.connect("task-database.db") # Создаем соединение с БД SQLite по указанному пути 
        self.cursor = self.con.cursor() # Создаем курсор - он позволит выполнять SQL-запросы к БД
        self.create_task_table() # Вызываем метод для создания таблицы задач, если ее еще нет

    # метод создает таблицу для хранения задач в БД
    def create_task_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY AUTOINCREMENT, task varcahr(50) NOT NULL, due_date varchar(50), completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)))")

    # метод создания задачи
    def create_task(self, task, due_date=None):
        self.cursor.execute("INSERT INTO tasks(task, due_date, completed) VALUES(?, ?, ?)", (task, due_date, 0))
        self.con.commit() # сохранение изменений в базе данных

        created_task = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE task = ? and completed = 0", (task,)).fetchall()
        return created_task[-1]

    def get_tasks(self):        
        complete_tasks = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE completed = 1").fetchall() # вставка задачи в базу данных
        incomplete_tasks = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE completed = 0").fetchall() # сохранение изменений в базе данных
        return complete_tasks , incomplete_tasks # Возвращает список незавершенных и завершенных задач
    
    # Метод принимает один аргумент taskid - идентификатор задачи, которую нужно отметить как завершенную   
    def mark_task_as_complete(self, taskid):
        self.cursor.execute("UPDATE tasks SET completed=1 WHERE id=?",(taskid,)) # Изменение значения столбца completed в таблице tasks на 1 для задачи с заданным идентификатором taskid
        self.con.commit() # Сохраняем изменения в базе данных после выполнения запроса

    # Метод принимает один аргумент taskid - идентификатор задачи, которую нужно отметить как незавершенную
    def mark_task_as_incomplete(self, taskid):
        self.cursor.execute("UPDATE tasks SET completed=0 WHERE id=?",(taskid,)) # Происходит изменение значения столбца completed таблицы tasks на 0 для задачи с указанным идентификатором taskid
        self.con.commit() # Cохраняет изменения в базе данных после выполнения запроса.    

        task_text = self.cursor.execute("SELECT task FROM tasks WHERE id=?", (taskid,)).fetchall() # После выполнения запроса с помощью метода execute() получаем список задач, где id равен taskid
        return task_text[0][0] # Возвращаем первую строку из списка в виде строки
    
    # Метод удаляет задачу с указанным идентификатором
    def delete_task(self, taskid):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (taskid,))
        self.con.commit() # Cохраняет изменения в базе данных после выполнения запроса.    
    
    # Метод закрывает соединение с базой данных
    def close_db_connection(self): 
        self.con.close()
    

    

    