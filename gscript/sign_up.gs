const api_url =
  "https://1zrqp9tgzh.execute-api.us-east-1.amazonaws.com/dev/register";

function onSubmit(event) {
  try {
    const formResponse = event.response;
    const itemResponses = formResponse
      .getItemResponses()
      .map((itemResponse) => ({
        question: itemResponse.getItem().getTitle(),
        response: itemResponse.getResponse(),
      }));

    const member = createMember(itemResponses);
    member.timestamp = String(Date.now());

    UrlFetchApp.fetch(api_url, {
      method: "post",
      payload: JSON.stringify(member),
    });
    console.log("Success");
  } catch (error) {
    console.log(error);
  }
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
    this.timestamp = "";
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
          member.department = "Law";
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
