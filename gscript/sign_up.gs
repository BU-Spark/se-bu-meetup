const api_url = "";

// const SCHOOL_QUESTIONS = [
//   'What is your name as it appears on your BU ID?',
//   'What is your preferred first name?',
//   'What is your BU ID?',
//   'What are your pronouns?',
//   'What is your BU email address?',
//   "Can you attend meetups near BU's Charles River Campus?",
//   'Are you in a Doctoral program (PhD, J.D. etc)',
//   'Which of the following Schools are you enrolled in?',
//   'Which Department or Program are you in?',
//   'Which Department or Program are you enrolled in?',
//   'Which Department or Program are you enrolled in?',
//   'What Department or Program are you enrolled in?',
//   'Which degree are you pursuing?',
//   'Which Department or Program are you enrolled in?',
//   'Which Department or Program are you enrolled in?',
//   'What Department or Program are you enrolled in?',
//   'What degree level are you currently pursuing at BU?',
//   'What is the name of your degree program?',
//   'Anything else you want to include?'
// ]

function onSubmit(event) {
  const formResponse = event.response;
  const itemResponses = formResponse.getItemResponses().map((itemResponse) => ({
    question: itemResponse.getItem().getTitle(),
    response: itemResponse.getResponse(),
  }));

  const member = createMember(itemResponses);

  console.log(member);

  // make api call to backend
  // UrlFetchApp.fetch(api_url, {
  //   method: "post",
  //   payload: member
  // })
}

class Member {
  constructor() {
    this.first_name = "";
    this.full_name = "";
    this.bu_id = "";
    this.email = "";
    this.school = "";
    this.department = "";
    this.phone_number = "";
  }
}

// Function that returns a member
// Talked with client about how they are currently aggregating the questions into certain properties and it seems it's just question by question
function createMember(itemResponses) {
  const member = new Member();
  for (let i = 0; i < itemResponses.length; i++) {
    const itemResponse = itemResponses[i];
    const [question, response] = [
      itemResponse["question"],
      itemResponse["response"],
    ];

    switch (question) {
      case "What is your name as it appears on your BU ID?":
        member.full_name = response;
        break;
      case "What is your preferred first name?":
        member.first_name = response;
        break;
      case "What is your BU ID?":
        member.bu_id = response;
        break;
      case "What is your BU email address?":
        member.email = response;
        break;
      case "What is your phone number?":
        member.phone_number = response;
        break;
      case "Are you in a Doctoral program (PhD, J.D. etc)":
        if (response == "No") {
          member.school = "Other";
        }
        break;
      case "Which of the following Schools are you enrolled in?":
        member.school = response;
        if (response == "Faculty of Computing & Data Sciences") {
          member.department = "Faculty of Computing & Data Sciences";
        } else if (response == "School of Law") {
          member.department = "School of Law";
        } else if (response == "Questrom School of Business") {
          member.department = "Business";
        } else if (response == "School of Social Work") {
          member.department = "Social Work";
        }
        break;
      case "Which Department or Program are you in?":
      case "Which Department or Program are you enrolled in?":
      case "What Department or Program are you enrolled in?":
      case "What is the name of your degree program?":
        member.department = response;
        break;
    }
  }
  return member;
}
