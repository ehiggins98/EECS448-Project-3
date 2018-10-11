function parseParameters(functionString) {
  let params = functionString.match(/\(.*\)/)[0];
  params = params.substr(1, params.length - 2);
  return params.split(', ');
}

module.exports = function(params, code) {
  let pattern = /function (\w*)/g;

  let output = [];
  let temp = console.log
  console.log = (val) => output.push(val);

  try {
    eval(code);
  }
  catch(err) {
    return { error: err.message };
  }

  let functions = code.match(pattern);
  let result = "";

  if(output.length == 0 && functions) {
    if(functions.includes("function main") && typeof main === typeof(Function)) {
      if(params) {
        result = main(...params);
      }
      else {
        result = main();
      }
    }
    else {
      let f = functions[0].substr(functions[0].indexOf(' ') + 1, functions[0].length);
      let regex = new RegExp(`function ${f} ?\(.*\) ?\{.*\}`);
      let functionString = code.match(regex)[0];
      if (eval(`typeof(${f}) == typeof(Function)`)) {
        let executable = new Function(...parseParameters(functionString), functionString.match(/\{.*\}/));
        if(params) {
          result = executable(...params)
        }
        else {
          result = executable();
        }
      }
    }
  }
  console.log = temp;

  if (result)
    output.push(result);
  return { result: output };
}
