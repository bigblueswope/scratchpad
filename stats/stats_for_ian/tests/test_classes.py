class Person(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def say_name(self):
        print(f"Hi! My name is {self.name}.")

    def say_age(self):
        print(f"I am {self.age} years old.")


tom = Person("Tom", 42)

tom.say_name()
tom.say_age()

print(f"Tommy's attributes name:{tom.name} age:{tom.age}")
