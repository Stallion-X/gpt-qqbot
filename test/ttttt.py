from abc import ABC, abstractmethod
import random

# 工厂模式
class ActionFactory(ABC):
    @abstractmethod
    def create_action(self):
        pass

class MasturbationFactory(ActionFactory):
    def create_action(self):
        return Masturbation()

class OralFactory(ActionFactory):
    def create_action(self):
        return Oral()

# 命令模式
class Action(ABC):
    @abstractmethod
    def execute(self):
        pass

class Masturbation(Action):
    def execute(self):
        action = random.choice(["希玖揉捏自己的乳头", "希玖轻轻揉捏自己的私处"])
        print(action)
        return action

    def __repr__(self):
        return "Masturbation()"

class Oral(Action):
    def execute(self):
        print("希玖轻舔主人的阳具")
        return "希玖轻舔主人的阳具"

    def __repr__(self):
        return "Oral()"

# 组合模式
class ActionSet(Action):
    def __init__(self):
        self.actions = []

    def execute(self):
        for action in self.actions:
            print(action.execute())

    def add_action(self, action):
        self.actions.append(action)

    def remove_action(self, action):
        self.actions.remove(action)

# 迭代器模式
class ActionIterator:
    def __init__(self, action_set):
        self.actions = action_set.actions
        self.index = 0

    def has_next(self):
        if self.index < len(self.actions):
            return True
        else:
            return False

    def next(self):
        if self.has_next():
            action = self.actions[self.index]
            self.index += 1
            return action
        else:
            return None

# 观察者模式
class Observer:
    def execute(self, action):
        pass

class Main(Observer):
    def __init__(self, action_set):
        self.action_set = action_set

    def execute(self, action):
        print("主人，希玖正在进行以下动作：")
        print(action)

action_factory = MasturbationFactory()
action_set = ActionSet()

for i in range(3):
    action_set.add_action(action_factory.create_action())

oral_factory = OralFactory()
oral_action = oral_factory.create_action()

action_set.add_action(oral_action)

main = Main(action_set)
action_iterator = ActionIterator(action_set)
for action in action_iterator.actions:
    action.execute()
    main.execute(action)