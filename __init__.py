import json
from adapt.intent import IntentBuilder
from os.path import join

from mycroft import intent_handler, FallbackSkill
from mycroft.util import normalize


class QuestionLearnerSkill(FallbackSkill):
    def __init__(self):
        super(QuestionLearnerSkill, self).__init__()
        if self.file_system.exists('entities.json'):
            with self.file_system.open('entities.json', 'r') as f:
                try:
                    self.entity_definitions = json.load(f)
                except ValueError:
                    self.entity_definitions = {}
        else:
            self.entity_definitions = {}

    def initialize(self):
        self.register_fallback(self.handle_fallback, 12)
        for i in self.entity_definitions:
            self.register_vocabulary(i, 'Entity')

    def add_entity(self, entity, definition):
        self.entity_definitions[entity] = definition
        with self.file_system.open('entities.json', 'w') as f:
            json.dump(self.entity_definitions, f, indent=4)
        for i in self.entity_definitions:
            self.register_vocabulary(i, 'Entity')

    @intent_handler(IntentBuilder('QuestionLearnerAnswer').require('Question').require('Entity'))
    def handle_question(self, message):
        entity = message.data['Entity']
        self.speak_dialog('question', {'entity': entity, 'description': self.entity_definitions[entity]})

    def voc_name(self, name):
        return join(self.vocab_dir, name + '.voc')

    def read_voc_lines(self, name):
        with open(self.voc_name(name)) as f:
            return filter(bool, map(str.strip, f.read().split('\n')))

    def handle_fallback(self, message):
        utterance = normalize(message.data['utterance']).lower()
        entity = None
        for l in self.read_voc_lines('Question'):
            if utterance.startswith(l.lower()):
                entity = utterance.replace(l, '').strip()
                break
        if not entity:
            return False

        description = self.get_response('respond.back', data={'entity': entity, 'question': utterance})
        if not description:
            return True

        for l in self.read_voc_lines('ItIs'):
            l = l.replace('{entity}', entity).lower()
            if description.startswith(l):
                description = description.replace(l, '').strip()
                break
        self.add_entity(entity, description)
        self.speak_dialog('new.info', data={'entity': entity, 'description': description})
        return True

def create_skill():
    return QuestionLearnerSkill()

