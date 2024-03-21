// Import required modules
const { Configuration, OpenAI } = require("openai");

// Define the main function for handling requests
exports.handler = async function(context, event, callback) {
    // Thread ID
    const threadId = event.threadId;
    console.log("Retrived", threadId)
    // Set up the OpenAI API with the API key
    const openai = new OpenAI({ apiKey: context.OPENAI_API_KEY });
    console.log("Registered", context.OPENAI_API_KEY)
    // Set up the Twilio VoiceResponse object to generate the TwiML
    const twiml = new Twilio.twiml.VoiceResponse();

    // Initiate the Twilio Response object to handle updating the cookie with the chat history
    const response = new Twilio.Response();

    // Parse the cookie value if it exists
    const cookieValue = event.request.cookies.convo;
    const cookieData = cookieValue ?
        JSON.parse(decodeURIComponent(cookieValue)) :
        null;

    // Get the user's voice input from the event
    let voiceInput = event.SpeechResult;
    console.log("User message", voiceInput)

    // Create a conversation variable to store the dialog and the user's input to the conversation history
    const conversation = cookieData?.conversation || [];
    conversation.push(`user: ${voiceInput}`);

    // Get the AI's response based on the conversation history
    const aiResponse = await generateAIResponse(threadId, voiceInput);

    // For some reason the OpenAI API loves to prepend the name or role in its responses, so let's remove 'assistant:' 'Joanna:', or 'user:' from the AI response if it's the first word
    const cleanedAiResponse = aiResponse.replace(/^\w+:\s*/i, "").trim();

    // Add the AI's response to the conversation history
    conversation.push(`assistant: ${aiResponse}`);

    // Limit the conversation history to the last 10 messages; you can increase this if you want but keeping things short for this demonstration improves performance
    while (conversation.length > 10) {
        conversation.shift();
    }

    // Generate some <Say> TwiML using the cleaned up AI response
    twiml.say({
            voice: "Polly.Joanna-Neural",
        },
        cleanedAiResponse
    );

    // Redirect to the Function where the <Gather> is capturing the caller's speech
    twiml.redirect({
            method: "POST",
        },
        `/transcribe`
    );

    // Since we're using the response object to handle cookies we can't just pass the TwiML straight back to the callback, we need to set the appropriate header and return the TwiML in the body of the response
    response.appendHeader("Content-Type", "application/xml");
    response.setBody(twiml.toString());

    // Update the conversation history cookie with the response from the OpenAI API
    const newCookieValue = encodeURIComponent(
        JSON.stringify({
            conversation,
        })
    );
    response.setCookie("convo", newCookieValue, ["Path=/"]);

    // Return the response to the handler
    return callback(null, response);

    // Function to generate the AI response based on the conversation history
    async function generateAIResponse(threadId, voiceInput) {
        return await createChatCompletion(threadId, voiceInput);
    }

    // Function to create a chat completion using the OpenAI API
    async function createChatCompletion(threadId, voiceInput) {
        try {
            const myThreadMessage = await openai.beta.threads.messages.create(
                    threadId,
                    {
                    role: "user",
                    content: voiceInput,
                    }
                );
            console.log("This is the message object: ", myThreadMessage, "\n");
            const myRun = await openai.beta.threads.runs.create(
                                threadId,
                                {
                                assistant_id: 'asst_HBm9X29io6tMuiphtvQeTuyh',
                                }
                            );
            const retrieveRun = async () => {
                            let keepRetrievingRun;

                            while (myRun.status !== "completed") {
                                keepRetrievingRun = await openai.beta.threads.runs.retrieve(
                                threadId, // Use the stored thread ID for this user
                                myRun.id
                                );

                                // console.log(`Run status: ${keepRetrievingRun.status}`);

                                if (keepRetrievingRun.status === "completed") {
                                console.log("\n");
                                break;
                                }
                            }
                            };
            await retrieveRun();

            const allMessages = await openai.beta.threads.messages.list(
                                threadId // Use the stored thread ID for this user
                                );
            console.log(allMessages['options'])
            console.log(allMessages['response'])
            console.log(allMessages['body'])
            console.log(allMessages.data[0].content[0].text.value)
            return allMessages.data[0].content[0].text.value;
        } catch (error) {
            // Check if the error is a timeout error
            if (error.code === "ETIMEDOUT" || error.code === "ESOCKETTIMEDOUT") {
                console.error("Error: OpenAI API request timed out."); // Log an error message indicating that the OpenAI API request timed out
                twiml.say({
                        // Create a TwiML say element to provide an error message to the user
                        voice: "Polly.Joanna-Neural",
                    },
                    "I'm sorry, but it's taking me a little bit too long to respond. Let's try that again, one more time."
                );
                twiml.redirect({
                        // Create a TwiML redirect element to redirect the user to the /transcribe endpoint
                        method: "POST",
                    },
                    `/transcribe`
                );
                response.appendHeader("Content-Type", "application/xml"); // Set the Content-Type header of the response to "application/xml"
                response.setBody(twiml.toString()); // Set the body of the response to the XML string representation of the TwiML response
                return callback(null, response); // Return the response to the callback function
            } else {
                console.error("Error during OpenAI API request:", error);
                throw error;
            }
        }
    }

    // Function to format the conversation history into a format that the OpenAI API can understand
    function formatConversation(conversation, threadId) {
        let isAI = true;
        const messages = [{
                role: "system",
                content: "You are a creative, funny, friendly and amusing AI assistant named Joanna. Please provide engaging but concise responses.",
            },
            {
                role: "user",
                content: "We are having a casual conversation over the telephone so please provide engaging but concise responses.",
            },
        ];

        // Iterate through the conversation history and alternate between 'assistant' and 'user' roles
        for (const message of conversation.split(";")) {
            const role = isAI ? "assistant" : "user";
            messages.push({
                role: role,
                content: message,
            });
            isAI = !isAI;
        }
        return messages;
    }
};