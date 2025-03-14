type Choice = {
    'id': number,
    'text': string,
    'correct': boolean
};

type Question = {
    id: number,
    text: string,
    choices: Choice[]
};

type Response = {
    question_id: number,
    answer_id: number,
    learner_id: string
};

type Learner = {
    learner_id: string,
    learner_name: string
};

type Message = Choice | Question | Response | Learner;
