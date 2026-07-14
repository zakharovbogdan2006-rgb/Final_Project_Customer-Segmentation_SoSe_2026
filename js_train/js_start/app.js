// const { Component } = require("react")

let students = []
let i = 0
while (i != 5){
    let student = {
    name : "",
    surname : "", 
    age : "", 
    greet : function(){
        console.log("hi " + this.name)
    }
    
}
    student.name = "a" + i;
    student.surname = "b"+ i;
    student.age = i;
    students.push(student)
    i++;
}
console.log(students)
    // function greet(){
//     console.log("hello" + name + surname)
// }

// const readline = require("readline")

// const rl = readline.createInterface({
//   input: process.stdin,
//   output: process.stdout
// })
// rl.question("What is yput name?", function(name)
// {
//     student.name = name

//     rl.question ("What is your surname?", function(surname){

//     student.surname = surname
//     console.log(student)
//     })
// })


// let message = [];
// let i = 0;
// while (i != 10){
//     message.push(i);
//     i++;
// }
// console.log(message);
// console.log(message.length);
// const readline = require("readline")
// const rl = readline.createInterface
// ({
//     input: process.stdin,
//     output: process.stdout
// })
// rl.question("a?", function(ina){
//     const a = Number(ina)
//     rl.question("b?", function(inb){
//         const b = Number(inb);
//         console.log(a+b)
//         console.log(a*b)
//         console.log(a/b)
//         rl.close
//     })
// })



// const readline = require("readline")
// const rl = readline.createInterface
// ({
//     input: process.stdin,
//     output: process.stdout
// })
// rl.question("enter age ", function(age){
//     if (age >= 18){
//         console.log("Adult")
//     }
//     else{
//         console.log("Minor")
//     }
//     rl.close()
// })

// let arr = ["a", "b", "c", "d", "e"]
// console.log(arr[0])
// console.log(arr[arr.length - 1 ])
// console.log(arr.length)

// let arr = []
// arr.push(Number(2))
// arr.push(Number(3))
// arr.push("a")
// arr.push("b")
// console.log(arr)