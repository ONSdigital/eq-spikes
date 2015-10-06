class Questionnaire(object):
    def __init__(self):
        self.questions = []
        self.index = 0
        self.current = None
        self.responses = {}
        self.completed = False

    def start(self):
        self.current = self.questions[self.index]

    """
    Called after validation
    """
    def next(self, response):
        if not self.hasNext():
            self.completed = True
            return

        # Branching
        if len(self.current.branch_conditions) > 0:
            for branch_condition in self.current.branch_conditions:
                if self.current.reference == branch_condition.trigger and response == branch_condition.state:
                    nextQuestionReference = branch_condition.target
                    self.index = self.getQuestionIndex(nextQuestionReference)
                    self.current = self.questions[self.index]
                    return

        # Next sequential question
        self.index = self.index + 1
        self.current = self.questions[self.index]

        if len(self.current.display_conditions) > 0:
            for condition in self.current.display_conditions:
                if self.responses[condition.trigger] == condition.state:
                    return
            # None of our display conditions are met, skip to next
            self.next(None)

        # check skip conditions
        if len(self.current.skip_conditions) > 0:
            for skip_condition in self.current.skip_conditions:
                if self.responses[skip_condition.trigger] == skip_condition.state:
                    self.next(None)

    def hasNext(self):
        return self.index + 1 < len(self.questions)

    def getQuestionIndex(self, reference):
        index = 0
        for question in self.questions:
            if question.reference == reference:
                return index
            index += 1


class Question(object):
    """
    Base class representing a question
    """

    def __init__(self, type, reference):
        self.type = None
        self.question_text = None
        self.reference = None
        self.display_properties = None
        self.validation = []
        self.parts = []
        self.children = []
        self.display_conditions = []
        self.skip_conditions = []
        self.branch_conditions = []

        self.type = type
        self.reference = reference

    def ask(self):
        print self.reference + ": " + self.question_text
        userinput = raw_input('Your answer: ')
        return userinput

class InputTextQuestion(Question):
    """
    InputText Question subclass
    """

    def __init__(self, reference):
        super(InputTextQuestion, self).__init__('InputTextQuestion', reference)

class RepeatingTypeQuestion(Question):
    """
    InputText Question subclass
    """

    def __init__(self, reference):
        super(RepeatingTypeQuestion, self).__init__('RepeatingTypeQuestion', reference)

    def ask(self):
        response = []

        for child in self.children:
            while True:
                _answer = self._ask(child)
                if _answer == 'q':
                    break
                response.append(_answer)

        return response

    def _ask(self, question):
        return question.ask()

class Option(object):
    """
    An option for multiple choice questions
    """

    def __init__(self, reference, value, label=None):
        self.reference = reference
        self.value = value
        self.label = label


class SelectOne(object):
    """
    SelectOne allows the select of  only one of the options
    """

    def __init__(self, *args):
        self.options = args


class MultipleChoiceQuestion(Question):
    """
    Multiple Choice Question
    """
    def __init__(self, reference):
        super(MultipleChoiceQuestion, self).__init__('MultipleChoiceQuestion', reference)

    def ask(self):
        print self.reference + ": " + self.question_text
        print "Please choose one of the following:"
        for option in self.parts.options:
            print option.value

        userinput = raw_input('Your answer: ')
        return userinput


class YesNoQuestion(MultipleChoiceQuestion):
    """
    Boolean Question type
    """
    def __init__(self, reference):
        super(YesNoQuestion, self).__init__(reference)
        self.parts = SelectOne(
            Option(reference + 'y', 'Yes'),
            Option(reference + 'n', 'No')
        )


class Condition(object):
    """
    Base Branching Condition
    """
    def __init__(self, *args):
        if len(args) == 3:
            self.target = args[0]
            self.trigger = args[1]
            self.state = args[2]

        if len(args) == 2:
            self.trigger = args[0]
            self.state = args[1]


class JumpTo(Condition):
    """
    Jump branching condition
    """
    def __init__(self, target, trigger, state):
        super(JumpTo, self).__init__(target, trigger, state)


class QuestionnaireRunner(object):
    def __init__(self, questionnaire):
        self.questionnaire = questionnaire

    def start(self):
        self.questionnaire.start()

        while not self.questionnaire.completed:
            response = self.ask(self.questionnaire.current)
            self.questionnaire.responses[self.questionnaire.current.reference] = response
            self.questionnaire.next(response)

        print "Completed!"
        print self.questionnaire.responses

    def ask(self, question):
        return question.ask()


# Main program
if __name__ == "__main__":

    # Question One
    q1 = MultipleChoiceQuestion('q1')
    q1.question_text = 'What is your favourite colour?'
    q1.parts = SelectOne(
        Option('q1a', 'Blue'),
        Option('q1b', 'Red'),
        Option('q1c', 'Yellow'),
    )
    q1.validation.append('required')
    q1.branch_conditions.append(
        JumpTo('q4', 'q1', 'Yellow')
    )

    # Question Two
    q2 = MultipleChoiceQuestion('q2')
    q2.question_text = "What colour blue do you prefer?"
    q2.parts = SelectOne(
        Option('q2a', 'Sky Blue'),
        Option('q2b', 'Royal Blue'),
        Option('q2c', 'Navy Blue'),
    )
    q2.validation.append(
        "required"
    )
    q2.display_conditions.append(
        Condition('q1', 'Blue')
    )


    # Question Three
    q3 = MultipleChoiceQuestion('q3')
    q3.question_text = 'What shade of red do you prefer?'
    q2.parts = SelectOne(
        Option('q3a', 'Crimson'),
        Option('q3b', 'Ruby'),
        Option('q3c', 'Scarlet'),
    )
    q3.validation.append(
        'required'
    )
    q3.display_conditions.append(
        Condition('q1', 'Red')
    )


    # Question Four
    q4 = YesNoQuestion('q4')
    q4.question_text = 'Do you have a crayon in this colour?'
    q4.validation.append(
        'required'
    )

    # Question Five
    q5 = InputTextQuestion('q5')
    q5.question_text = 'What is your name?'

    # Question Six
    q6 = YesNoQuestion('q6')
    q6.question_text = 'Do you have children?'
    q6.validation.append(
        'required'
    )

    q7 = RepeatingTypeQuestion('q7')
    q7.question_text = 'What are the names of your children?'

    q7_1 = InputTextQuestion('q7_1')
    q7_1.question_text= 'Name? (q to quit)'

    q7.children.append(q7_1)


    ###
    #
    # create the questionnaire
    #
    ###
    questionnaire = Questionnaire()
    questionnaire.questions.append(q1)
    questionnaire.questions.append(q2)
    questionnaire.questions.append(q3)
    questionnaire.questions.append(q4)
    questionnaire.questions.append(q5)
    questionnaire.questions.append(q6)
    questionnaire.questions.append(q7)
    questionnaire.questions.append(q6)

    runner = QuestionnaireRunner(questionnaire)
    runner.start()
