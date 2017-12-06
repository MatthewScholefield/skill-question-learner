from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler


class QuestionLearnerSkill(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler(IntentBuilder().require('QuestionLearner'))
    def handle_question_learner(self, message):
        self.speak_dialog('question.learner')


def create_skill():
    return QuestionLearnerSkill()

