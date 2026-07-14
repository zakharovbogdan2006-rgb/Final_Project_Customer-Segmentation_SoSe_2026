const readline = require("readline")
const rl = readline.createInterface({
    input: process.stdin,
  output: process.stdout
})

function timer() {
    rl.question("Enter num: ", (num) => {
        console.log("Start");
        setTimeout((
        ) => {
    console.log("end");
    }, num);


        rl.close();
    });
}

timer();
