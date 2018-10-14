let {VM} = require('vm2');

class MyConsole {
  constructor() {
    this.outputs = [];
  }
  log(val) {
    this.outputs.push(val);
  }
}

function parseParameters(functionString) {
  let params = functionString.match(/\([^\{]*\)/)[0];
  params = params.substr(1, params.length - 2);
  return params.split(/[, ]/);
}

function aggregate(functions) {
  let code = "";
  functions.forEach(f => code += f.charAt(f.length - 1) === ";" ? f : f + ";");
  return code;
}

function runCode(code) {
  let myConsole = new MyConsole();
  const vm = new VM({
    timeout: 1000,
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

function runRaw(functions) {
  return runCode(aggregate(functions));
}

function runFunction(params, functions) {
  let paramNames = parseParameters(functions[1]);
  functions[1] = functions[1].substr(functions[1].indexOf("{")+1);
  for (let i = 0; i < paramNames.length && i < params.length; i++) {
    functions[1] = `let ${paramNames[i]} = ${params[i]};` + functions[1];
  }
  functions[1] = `function main() {${functions[1]} main()`;

  return runCode(aggregate(functions));
}

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

module.exports = function (params, code) {
  let functions = parseFunctions(code);
  if (functions[0] !== "") {
    return runRaw(functions);
  }
  else {
    return runFunction(params, functions);
  }
}
