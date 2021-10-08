/* * * * * * * * * * * * * *
*           MAIN           *
* * * * * * * * * * * * * */

// Helper function to score words
function score(word) {
    const isPangram = (new Set(word.split(""))).size == 7;

    // Scoring system: 1 point for 4-letter words, then 1 point per letter for longer words
    // (and 7-point bonus for pangrams)
    if (word.length == 4) {
        return 1;
    } else {
        return word.length + 7*(isPangram);
    }
}

// Function to validate words
// String is the string to be validated, letters is the list of valid letters (with the special one first)
function validate(string, letters, alreadyFound) {
    try {
        // First: check if contains any invalid letters
        const importantLetter = letters[0];

        // Removes duplicate letters
        const stringStripped = Array.from(new Set(string.split("")));

        // Test if there are any invalid characters
        if (!stringStripped.every(val => letters.includes(val))) {
            throw new Error("Invalid Characters");
            // Test if this includes special character
        } else if (!stringStripped.includes(importantLetter)) {
            throw new Error("Doesn't Contain Center Letter");
            // Test if the word is too short
        } else if (string.length < 4) {
            throw new Error("Too short");
        } else if (alreadyFound.includes(string)) {
            throw new Error("Already found");
        } else {
            return "Good";
        }
    }
    catch(e) {
        return e.message;
    }
}

// Main function
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("guess-field").autofocus = true;

    let submitButton = document.querySelector(".submit-button");

    const scoreElem = document.getElementsByClassName("score-span")[0];
    const wordlistElem = document.querySelector(".found-words");

    const messageDiv = document.getElementById("message-div");

    // Load in the letters
    const submitId = submitButton.id.split("-")[1];

    // Get the initial score and word list
    getWords(submitId).then(response => {
        scoreElem.innerText = response[1];
        createList(wordlistElem, response[0]);
    });

    fetch(`letters/${submitId}`, {
        method: 'GET'
    })
        .then(response => response.json())
        .then(result => {

            // Get the list of letters
            const letterList = result.all.split("");
            submitButton.addEventListener('click', function() {
                const guess = document.getElementById("guess-field").value.toUpperCase();

                getWords(submitId).then(response => {
                    let foundScore = response[1];
                    let foundWords = response[0];
                    // Validate the guess
                    const guessAlert = validate(guess, letterList, foundWords);

                    // Check basic errors
                    if (guessAlert == "Good") {
                        // Use the dictionaryapi to see if the guess is counted as a word
                        fetch("https://api.dictionaryapi.dev/api/v2/entries/en_US/" + guess, {
                            "method": "GET",
                        })
                            .then(response => {
                                if (response.status >= 200 && response.status <= 299) {

                                    // Score the word
                                    const guessScore = score(guess);

                                    // Create a word object, then update the divs
                                    createWord(guess, submitId).then(() => {
                                        foundWords.push(guess);
                                        createList(wordlistElem, foundWords);
                                        scoreElem.innerText = (foundScore + guessScore);
                                    });

                                    displayMessage(messageDiv, "Nice! Points: " + guessScore.toString());

                                } else {
                                    displayMessage(messageDiv, "Word not found");
                                    throw Error("Word not found");
                                }
                            })
                            .catch(err => {
                                console.error(err);
                            });
                    } else {
                        displayMessage(messageDiv, guessAlert);
                    }
                    // Reset guess field, and focus back on the text field
                    document.getElementById("guess-field").value = "";
                    document.getElementById("guess-field").focus();

                });
            });
        });

    // Additionally, add an event listener to each "button" that adds to the text field when clicked
    let letterButtons = document.querySelectorAll('.boxed');

    letterButtons.forEach(function(button) {

        button.addEventListener('click', function() {
            const buttonId = button.id;

            let guessText = document.getElementById("guess-field");

            guessText.value = guessText.value + buttonId;
        });
    });
});

// Function that creates a new Word object using an API call
function createWord(word, puzId) {
    // API call to create a new word
    return fetch('/puzzles/new_word', {
        method: "POST",
        body: JSON.stringify( {
            word: word,
            puzId: puzId,
        })
    })
        .then(response => response.json())
        .then(result => {console.log(result);});
}

// Function that returns a list of words, followed by the total score
function getWords(puz_id) {
    // API call to get the list of words for a user
    return fetch(`getwords/${puz_id}`)
        .then(response => response.json())
        .then(result => {

            // Things to fill
            let wordlist = [];
            let totalScore = 0;

            // Given the result of the API call (which is a list of Word objects),
            // create a list of words and a score
            const res = JSON.parse(result);
            res.forEach(word => {
                const wordText = word['fields']['text'];
                const wordScore = score(wordText);
                totalScore += wordScore;
                wordlist.push(wordText);
            });
            return([wordlist, totalScore]);
        });
}

// Function that creates a list of words in an element
function createList(elem, wordlist) {
    elem.innerHTML = "";
    wordlist.sort();
    wordlist.forEach(word => {
        elem.append(word);
        let linebreak = document.createElement("br");
        elem.append(linebreak);
    });
}

// Function that briefly populates an element with an alert
function displayMessage(elem, message) {
    elem.innerHTML = message;
    elem.style.display = "block";
    setTimeout(function () {
        elem.style.display = "none";
    }, 750);
}