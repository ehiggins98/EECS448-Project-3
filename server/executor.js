function parseParameters(functionString) {
  let params = functionString.match(/\([^\{]\)/)[0];
  params = params.substr(1, params.length - 2);
  return params.split(', ');
}

module.exports = function(params, code) {
  let pattern = /function (\w*)/g;
  let output = [];
  console.log = (val) => output.push(val);
  try {
    eval(code);
  }
  catch(err) {
    return { error: err.message };
  }

  let functions = code.match(pattern);
  let executable = null;

  if(output.length == 0 && functions) {
    if(functions.includes("function main") && typeof main === typeof(Function)) {
      executable = main;
    }
    else {
      let f = functions[0].substr(functions[0].indexOf(' ') + 1, functions[0].length);
      let regex = new RegExp(`function ${f} ?\(.*\) ?\{.*\}`);
      if (eval(`typeof(${f}) === typeof(Function)`)) {
        let functionString = code.match(regex)[0];
        executable = new Function(...parseParameters(functionString), functionString.match(/\{.*\}/));
      }
    }
  }
  try {
    if (executable) {
      let result = params ? executable(...params) : executable();
      console.log = temp;
      if (result)
        output.push(result);
    }
    return { result: output };
  }
  catch(err) {
    console.log = temp;
    return { error: err.message };
  }
}
