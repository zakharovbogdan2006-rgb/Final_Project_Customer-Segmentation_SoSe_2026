var typer = (function(value) {
  
  return {
isNumber: function(value) {
  if (typeof value === "number") {
    return !Number.isNaN(value);
  }

  if (value instanceof Number) {
    return !Number.isNaN(value.valueOf());
  }

  return false;
},
    isString: function(value){
      return (typeof value === "string" || value instanceof String);
      }
    ,
    isArray: function(value){
      return (typeof value === "array" || value instanceof Array);
      },
    isFunction: function(value){
      return (typeof value === "function" || value instanceof Function)
    },
    isDate: function(value){
      return (typeof value === "date" || value instanceof Date)}
    ,
    isRegExp: function(value){
      return (typeof value === "regexr"|| value instanceof RegExp)}
    ,
    isBoolean: function(value){
      return (typeof value === "boolean" || value instanceof Boolean)}
    ,
    isError: function(value){
      return (typeof value === "error" || value instanceof Error)}
    ,
    isNull: function(value){
      return ( value === null)}
    ,
    isUndefined: function(value){
      return (typeof value === "undefined")}

  };
}(null));