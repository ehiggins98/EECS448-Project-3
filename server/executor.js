let {VM} = require('vm2');

/**
 * Collects console output from the VM.
 */
class MyConsole {
  constructor() {
    this.outputs = [];
  }
  log(val) {
    this.outputs.push(val);
  }
}

/**
 * Parses parameters from either a function declaration or function declaration and body.
 * @param {string} functionString The function string to parse.
 * @returns An array of parameters to the function.
 */
function parseParameters(functionString) {
  let params = functionString.match(/\([^\{]*\)/)[0];
  params = params.substr(1, params.length - 2);
  return params.split(/[, ]/);
}

/**
 * Aggregates an array of function strings into a single code string.
 * @param {string[]} functions The array of function strings to combine.
 * @returns A string containing all the given functions.
 */
function aggregate(functions) {
  let code = "";
  functions.forEach(f => code += f.charAt(f.length - 1) === ";" ? f : f + ";");
  return code;
}

/**
 * Runs the code in a VM.
 * @param {string} code A string representation of the code to execute. 
 * @return {string[]} An array containing the outputs from code execution.
 */
function runCode(code) {
  try {
    let myConsole = new MyConsole();
    const vm = new VM({
      timeout: 5000,
      sandbox: {
        console: myConsole
      }
    });

    let result = vm.run(code);
    if (result !== undefined) {
      myConsole.outputs.push(result);
    }

    return myConsole.outputs;
  }
  catch (error) {
    console.log(error.message);
    return [ error.message ];
  }
}

/**
 * Runs code raw (i.e. doesn't parse any functions to execute).
 * @param {string[]} functions An array of function strings and code outside of functions to execute.
 * @return {string[]} An array containing outputs from the code execution.
 */
function runRaw(functions) {
  return runCode(aggregate(functions));
}

/**
 * Parses out a function to run and executes the code
 * @param {string[]} params The parameters supplied by the user to pass to the function.
 * @param {functions[]} functions An array of function strings to execute.
 * @return {string[]} An array containing outputs from the code execution.
 */
function runFunction(params, functions) {
  let paramNames = parseParameters(functions[1]);
  functions[1] = functions[1].substr(functions[1].indexOf("{")+1);
  for (let i = 0; i < paramNames.length && i < params.length; i++) {
    functions[1] = `let ${paramNames[i]} = ${params[i]};` + functions[1];
  }
  functions[1] = `function main() {${functions[1]} main()`;

  return runCode(aggregate(functions));
}

/**
 * Parses a given string of code into functions.
 * @param {string} code A string representation of the code to execute.
 * @return {string[]} An array containing functions and code outside of all functions, represented as a string.
 */
function parseFunctions(code) {
  let functions = [""];
  let inTopLevelFunction = false;
  let braceCounter = 0;
  let mainIndex = 1;

  let lines = code.split(/(?<=[;\n\r\{\}]\s*)/g);

  for (let i = 0; i < lines.length; i++) {
    lines[i] = lines[i].trim();
    if (lines[i].length > 8 && (lines[i].substr(0, 8) === "function") && !inTopLevelFunction && braceCounter == 0) {
      mainIndex = lines[i].length > 13 && lines[i].substr(9, 13) === "main" ? i : mainIndex;

      functions.push(lines[i]);
      inTopLevelFunction = true;
    }
    else if (inTopLevelFunction) {
      functions[functions.length - 1] += lines[i];
    }
    else {
      functions[0] += lines[i];
    }
    braceCounter += (lines[i].match(/\{/g)||[]).length;
    braceCounter -= (lines[i].match(/\}/g)||[]).length;
    inTopLevelFunction = inTopLevelFunction && braceCounter !== 0;
  }

  if (mainIndex > 1) {
    let temp = functions[1];
    functions[1] = functions[mainIndex];
    functions[mainIndex] = temp;
  }
  return functions;
}

/**
 * Executes code with the given parameters.
 * @param {string[]} params The parameters supplied by the user to pass to the code.
 * @param {string} code A string representation of the code to execute.
 * @return {string[]} An array containing the outputs from the code execution.
 */
module.exports = function (params, code) {
  let functions = parseFunctions(code);
  if (functions[0] !== "") {
    return runRaw(functions);
  }
  else {
    return runFunction(params, functions);
  }
}
