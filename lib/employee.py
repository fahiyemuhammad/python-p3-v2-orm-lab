from __init__ import CURSOR, CONN
from department import Department

class Employee:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return (
            f"<Employee {self.id}: {self.name}, {self.job_title}, " +
            f"Department ID: {self.department_id}>"
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str) and len(name):
            self._name = name
        else:
            raise ValueError("Name must be a non-empty string")

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, job_title):
        if isinstance(job_title, str) and len(job_title):
            self._job_title = job_title
        else:
            raise ValueError("job_title must be a non-empty string")

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, department_id):
        if type(department_id) is int and Department.find_by_id(department_id):
            self._department_id = department_id
        else:
            raise ValueError("department_id must reference a department in the database")

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Employee instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Employee instances."""
        sql = "DROP TABLE IF EXISTS employees;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row for this Employee object and store it in the dictionary."""
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        """Update the table row corresponding to the current Employee instance."""
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row, remove from dictionary, and set id to None."""
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        del type(self).all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, job_title, department_id):
        """Initialize and save a new Employee instance."""
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        """Return an Employee object from the database row."""
        employee = cls.all.get(row[0])
        if employee:
            employee.name = row[1]
            employee.job_title = row[2]
            employee.department_id = row[3]
        else:
            employee = cls(row[1], row[2], row[3])
            employee.id = row[0]
            cls.all[employee.id] = employee
        return employee

    @classmethod
    def get_all(cls):
        """Return a list of all Employee objects from the database."""
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Return Employee by ID."""
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Return Employee by name."""
        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def reviews(self):
        """Return list of reviews associated with this employee."""
        from review import Review  # Avoid circular import
        return [review for review in Review.all.values() if review.employee_id == self.id]