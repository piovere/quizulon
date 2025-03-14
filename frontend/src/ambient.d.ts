type Choice = {
    'id': number,
    'text': string,
    'correct': boolean,
    message_type: string
};

type Question = {
    id: number,
    text: string,
    choices: Choice[],
    message_type: string
};

type Response = {
    question_id: number,
    answer_id: number,
    learner_id: string,
    message_type: string
};

type Learner = {
    learner_id: string,
    learner_name: string,
    message_type: string
};

type Data = {
    questions: Question[],
    learners: Learner[],
    responses: Response[],
    message_type: null
};

type Message = Choice | Question | Response | Learner | Data;
